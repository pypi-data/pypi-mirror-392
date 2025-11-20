import requests

from django.contrib import messages
from django.contrib.contenttypes.fields import GenericRel
from django.core.exceptions import FieldDoesNotExist, ValidationError, ObjectDoesNotExist
from django.db import transaction, connection
from django.db.models import ManyToManyField, ManyToManyRel, F, Q, Func, Value
from django.db.models.fields.json import KeyTextTransform
from django.utils.decorators import method_decorator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from .. import get_config, forms, importer, models, tables
from ..models import SlurpitImportedDevice, SlurpitSetting, add_default_mandatory_objects
from ..management.choices import *
from ..importer import get_dcim_device, import_from_queryset, run_import, get_devices, BATCH_SIZE, import_devices, process_import, start_device_import, sync_locations
from ..decorators import slurpit_plugin_registered
from ..references import base_name, custom_field_data_name
from ..references.generic import create_form, get_form_device_data, SlurpitViewMixim, get_default_objects, set_device_custom_fields, status_inventory, status_active_for_interface, status_active_for_ipaddress, status_active_for_prefix, get_create_dcim_objects, status_active
from ..references.imports import * 

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from ..filtersets import SlurpitImportedDeviceFilterSet
from django.db.models.functions import Cast, Substr
from django.db.models import TextField
import netaddr
class TrimCIDR(Func):
    function = 'substring'
    template = "%(function)s(%(expressions)s FROM 1 FOR POSITION('/' IN %(expressions)s) - 1)"

class IpToBytea(Func):
    function = 'inet'
    template = "%(function)s(%(expressions)s)"

@method_decorator(slurpit_plugin_registered, name='dispatch')
class SlurpitImportedDeviceListView(SlurpitViewMixim, generic.ObjectListView):    
    onboarded_queryset = models.SlurpitImportedDevice.objects.filter(mapped_device_id__isnull=False)
    migrate_queryset = models.SlurpitImportedDevice.objects.filter(
                mapped_device_id__isnull=False
            ).annotate(
                slurpit_devicetype=KeyTextTransform('slurpit_devicetype', 'mapped_device__' + custom_field_data_name),
                slurpit_hostname=KeyTextTransform('slurpit_hostname', 'mapped_device__' + custom_field_data_name),
                slurpit_fqdn=KeyTextTransform('slurpit_fqdn', 'mapped_device__' + custom_field_data_name),
                slurpit_platform=KeyTextTransform('slurpit_platform', 'mapped_device__' + custom_field_data_name),
                slurpit_manufacturer=KeyTextTransform('slurpit_manufacturer', 'mapped_device__' + custom_field_data_name),
                slurpit_ipv4=KeyTextTransform('slurpit_ipv4', 'mapped_device__' + custom_field_data_name),
                slurpit_location=KeyTextTransform('slurpit_location', 'mapped_device__' + custom_field_data_name),
                fdevicetype=F('device_type'),
                fhostname=F('hostname'),
                ffqdn=F('fqdn'),
                fipv4=F('ipv4'),
                fdeviceos=F('device_os'),
                fbrand=F('brand'),
                flocation=F('location')
            ).exclude(
                Q(slurpit_devicetype=F('fdevicetype')) & 
                Q(slurpit_hostname=F('fhostname')) & 
                Q(slurpit_fqdn=F('ffqdn')) & 
                Q(slurpit_platform=F('fdeviceos')) & 
                Q(slurpit_manufacturer=F('fbrand')) &
                Q(slurpit_ipv4=F('fipv4')) &
                Q(slurpit_location=F('flocation'))
            )
    
    queryset = onboarded_queryset

    action_buttons = []
    table = tables.SlurpitImportedDeviceTable
    template_name = f"{base_name}/onboard_device.html"
    filterset = SlurpitImportedDeviceFilterSet

    def get(self, request, *args, **kwargs):  
        self.conflicted_queryset = models.SlurpitImportedDevice.objects.filter(
            mapped_device_id__isnull=True
        ).conflicted_devices()
        self.to_onboard_queryset = models.SlurpitImportedDevice.objects.filter(mapped_device_id__isnull=True).exclude(pk__in=self.conflicted_queryset.values('pk'))
    
         
        if request.GET.get('tab') == "migrate":
            self.queryset = self.migrate_queryset
            self.table = tables.MigratedDeviceTable
        elif request.GET.get('tab') == "conflicted":
            self.queryset = self.conflicted_queryset
            self.table = tables.ConflictDeviceTable
        elif request.GET.get('tab') == "onboarded":
            self.table = tables.SlurpitOnboardedDeviceTable
            self.queryset = self.onboarded_queryset
        else:
            self.table = tables.SlurpitImportedDeviceTable
            self.queryset = self.to_onboard_queryset

        return super().get(request, *args, **kwargs)
    
    def post(self, request):
        self.conflicted_queryset = models.SlurpitImportedDevice.objects.filter(
            mapped_device_id__isnull=True
        ).conflicted_devices()
        
        self.to_onboard_queryset = models.SlurpitImportedDevice.objects.filter(mapped_device_id__isnull=True).exclude(pk__in=self.conflicted_queryset.values('pk'))
        self.queryset = self.to_onboard_queryset
        self.table = tables.SlurpitImportedDeviceTable
        if request.POST.get('_all'):
            qs = self.queryset
        else:
            pks = map(int, request.POST.getlist('pk'))
            qs = self.queryset.filter(pk__in=pks, mapped_device_id__isnull=True)

        import_from_queryset(qs)

        return redirect(request.path)

    def slurpit_extra_context(self):
        appliance_type = ''
        connection_status = ''
        try:
            setting = SlurpitSetting.objects.get()
            server_url = setting.server_url
            api_key = setting.api_key
            appliance_type = setting.appliance_type
            connection_status = setting.connection_status
        except ObjectDoesNotExist:
            setting = None

        total = SlurpitImportedDevice.objects.all()

        return {
            'to_onboard_count': self.to_onboard_queryset.count(),
            'onboarded_count': self.onboarded_queryset.count(),
            'migrate_count': self.migrate_queryset.count(),
            'conflicted_count': self.conflicted_queryset.count(),
            'appliance_type': appliance_type,
            'connection_status': connection_status,
            **self.slurpit_data
        }


@method_decorator(slurpit_plugin_registered, name='dispatch')
class SlurpitImportedDeviceOnboardView(SlurpitViewMixim, generic.BulkEditView):
    template_name = f"{base_name}/bulk_edit.html"
    queryset = models.SlurpitImportedDevice.objects.all()
    table = tables.SlurpitImportedDeviceTable
    model_form = forms.OnboardingForm
    form = forms.OnboardingForm
    filterset = SlurpitImportedDeviceFilterSet

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['models_queryset'] = self.queryset
        return kwargs

    def post(self, request, **kwargs):
        model = self.queryset.model

        if request.POST.get('_all') and self.filterset is not None:
            pk_list = self.filterset(request.GET, self.queryset.values_list('pk', flat=True), request=request).qs
            self.queryset = models.SlurpitImportedDevice.objects.all()
        else:
            pk_list = request.POST.getlist('pk')
            self.queryset = models.SlurpitImportedDevice.objects.filter(pk__in=pk_list)

         # Remove
        if 'remove' in request.GET:
            if len(pk_list) == 0:
                messages.warning(request, "No {} were selected.".format(model._meta.verbose_name_plural))
                log_message = "Failed to remove since no devices were selected."
                
            else:
                if 'onboarded' in request.GET:
                    for onboarded_item in self.queryset:
                        cf = onboarded_item.mapped_device._custom_field_data
                        cf.pop('slurpit_hostname')
                        cf.pop('slurpit_fqdn')
                        cf.pop('slurpit_platform')
                        cf.pop('slurpit_manufacturer')
                        cf.pop('slurpit_devicetype')
                        cf.pop('slurpit_ipv4')
                        cf.pop('slurpit_location')
                        onboarded_item.mapped_device._custom_field_data = cf
                        onboarded_item.mapped_device.save()

                self.queryset.delete()
                msg = f'Removed {len(pk_list)} {model._meta.verbose_name_plural}'
                messages.success(self.request, msg)
            return redirect(self.get_return_url(request))

        device_types = list(self.queryset.values_list('device_type').distinct())
        locations = list(self.queryset.values_list('location').distinct())

        form = create_form(self.form, request.POST, models.SlurpitImportedDevice, {'pk': pk_list, 'device_types': device_types, 'locations': locations})
        restrict_form_fields(form, request.user)

        if '_apply' in request.POST:
            if form.is_valid():
                try:
                    with transaction.atomic():
                        updated_objects, status, error, obj_name = self._update_objects(form, request)
                        
                        if status == "fail":
                            msg = f'{error[0:-1]} at {obj_name}.'
                            messages.error(self.request, msg)
                            return redirect(self.get_return_url(request))

                        if updated_objects:
                            msg = f'Onboarded {len(updated_objects)} {model._meta.verbose_name_plural}'
                            messages.success(self.request, msg)

                    return redirect(self.get_return_url(request))

                except ValidationError as e:
                    messages.error(self.request, ", ".join(e.messages))
                    # clear_webhooks.send(sender=self)
                    return JsonResponse({"status": "error", "error": str(e)})
                
                except Exception as e:
                    messages.error(self.request, str(e))
                    form.add_error(None, str(e))
                    # clear_webhooks.send(sender=self)
                    return JsonResponse({"status": "error", "error": str(e)})
                
            return JsonResponse({"status": "error", "error": "validation error"}) 

        elif 'migrate' in request.GET:
            migrate = request.GET.get('migrate')
            if migrate == 'create':                
                for obj in self.queryset:
                    device = obj.mapped_device
                    obj.mapped_device = None
                    obj.save()
                    device.delete() #delete last to prevent cascade delete
            elif migrate == 'update_slurpit':
                for obj in self.queryset:
                    device = obj.mapped_device
                    device.name = obj.hostname
                    set_device_custom_fields(device, {
                        'slurpit_hostname': obj.hostname,
                        'slurpit_fqdn': obj.fqdn,
                        'slurpit_platform': obj.device_os,
                        'slurpit_manufacturer': obj.brand,
                        'slurpit_devicetype': obj.device_type,
                        'slurpit_ipv4': obj.ipv4,
                        'slurpit_location': obj.location
                    })               

                    # Update Location           
                    defaults = get_default_objects()
                    location = defaults['location']

                    if obj.location is not None and obj.location != "":
                        location = Location.objects.get(name=obj.location)
                        device.location = location

                    device.save()
                    
                    log_message = f"Migration of onboarded device - {obj.hostname} successfully updated."
                    
                msg = f'Migration is done successfully.'
                messages.success(self.request, msg)

                return redirect(self.get_return_url(request))
            else:
                for obj in self.queryset:
                    device = obj.mapped_device
                    device.name = obj.hostname
                    set_device_custom_fields(device, {
                        'slurpit_hostname': obj.hostname,
                        'slurpit_fqdn': obj.fqdn,
                        'slurpit_platform': obj.device_os,
                        'slurpit_manufacturer': obj.brand,
                        'slurpit_devicetype': obj.device_type,
                        'slurpit_ipv4': obj.ipv4,
                        'slurpit_location': obj.location
                    })              

                    # Update Location           
                    defaults = get_default_objects()
                    if obj.location is not None and obj.location != "":
                        location = Location.objects.filter(name=obj.location).first()
                        if not location:
                            location = defaults['location']

                        device.location = location

                    device.device_type = get_create_dcim_objects(obj)
                    device.platform = Platform.objects.get(name=obj.device_os)
                    # if device.device_type:
                    #     device.platform = device.device_type.default_platform

                    device.save()
                    obj.save()

                    # Interface
                    if obj.ipv4:
                        address = f'{obj.ipv4}/32'
                        #### Remove Primary IPv4 on other device
                        other_device = Device.objects.annotate(
                            primary_ip4_host_str=Func(F('primary_ip4__host'), Value('escape'), function='encode', output_field=models.CharField())
                        ).filter(
                            primary_ip4_host_str=obj.ipv4
                        ).first()

                        if other_device:
                            other_device.primary_ip4 = None
                            other_device.save()

                        interface = Interface.objects.filter(device=device)
                        if interface:
                            interface = interface.first()
                        else:
                            interface = Interface.objects.create(name='management1', device=device, type='other', status=status_active_for_interface())

                        ipaddress = IPAddress.objects.filter(address=address)
                        if ipaddress:
                            ipaddress = ipaddress.first()
                        else:
                            Prefix.objects.get_or_create(prefix=address, defaults={'status':status_active_for_prefix()})
                            ipaddress = IPAddress.objects.create(address=address, status=status_active_for_ipaddress())
                        
                        ipaddress.assigned_object = interface
                        ipaddress.save()
                        device.primary_ip4 = ipaddress
                        device.save()

                    log_message = f"Migration of onboarded device - {obj.hostname} successfully updated."
                    
                msg = f'Migration is done successfully.'
                messages.success(self.request, msg)

                return redirect(self.get_return_url(request))

        elif 'conflicted' in request.GET:
            conflic = request.GET.get('conflicted')
            if conflic == 'create':
                Device.objects.filter(name__in=self.queryset.values('hostname')).delete()
            elif conflic == 'update_slurpit':
                for obj in self.queryset:
                    device = Device.objects.filter(name__iexact=obj.hostname).first()

                    # Management IP Case
                    if device is None:
                        masked_hosts = bytes(netaddr.IPNetwork(f'{obj.ipv4}/32').ip)
                        masked_prefixes = netaddr.IPNetwork(f'{obj.ipv4}/32').prefixlen
                        device = Device.objects.filter(Q(primary_ip4__host=masked_hosts, primary_ip4__mask_length=masked_prefixes)).first()

                    set_device_custom_fields(device, {
                        'slurpit_hostname': obj.hostname,
                        'slurpit_fqdn': obj.fqdn,
                        'slurpit_platform': obj.device_os,
                        'slurpit_manufacturer': obj.brand,
                        'slurpit_devicetype': obj.device_type,
                        'slurpit_ipv4': obj.ipv4,
                        'slurpit_location': obj.location
                    })      
                    other_imported_device = SlurpitImportedDevice.objects.filter(mapped_device=device).first()
                    if other_imported_device:
                        other_imported_device.delete()

                    obj.mapped_device = device    

                    # Update Location           
                    defaults = get_default_objects()
                    if obj.defaults is not None and obj.defaults != "":
                        location = Location.objects.filter(name=obj.location).first()
                        if not location:
                            location = defaults['location']
                        device.location = location

                    device.save()
                    obj.save()

                    log_message = f"Conflicted device resolved - {obj.hostname} successfully updated."
                    
                msg = f'Conflicts successfully resolved.'
                messages.success(self.request, msg)

                return redirect(self.get_return_url(request))
            
            else:
                for obj in self.queryset:
                    device = Device.objects.filter(name__iexact=obj.hostname).first()

                    # Management IP Case
                    if device is None:
                        masked_hosts = bytes(netaddr.IPNetwork(f'{obj.ipv4}/32').ip)
                        masked_prefixes = netaddr.IPNetwork(f'{obj.ipv4}/32').prefixlen
                        device = Device.objects.filter(Q(primary_ip4__host=masked_hosts, primary_ip4__mask_length=masked_prefixes)).first()
                    else:
                        if device.name != obj.hostname:
                            other_device = Device.objects.filter(name__iexact=obj.hostname).first()
                            if other_device:
                                other_device.delete()
                            
                            device.name = obj.hostname
                    set_device_custom_fields(device, {
                        'slurpit_hostname': obj.hostname,
                        'slurpit_fqdn': obj.fqdn,
                        'slurpit_platform': obj.device_os,
                        'slurpit_manufacturer': obj.brand,
                        'slurpit_devicetype': obj.device_type,
                        'slurpit_ipv4': obj.ipv4,
                        'slurpit_location': obj.location
                    })      

                    other_imported_device = SlurpitImportedDevice.objects.filter(mapped_device=device).first()
                    if other_imported_device:
                        other_imported_device.delete()

                    obj.mapped_device = device    

                    device.device_type = get_create_dcim_objects(obj)
                    device.platform = Platform.objects.get(name=obj.device_os)
                    # if device.device_type:
                    #     device.platform = device.device_type.default_platform

                    # Update Location           
                    defaults = get_default_objects()
                    location = defaults['location']
                    if obj.location is not None and obj.location != "":
                        location = Location.objects.get(name=obj.location)
                        device.location = location

                    device.save()
                    obj.save()

                    # Interface
                    if obj.ipv4:
                        address = f'{obj.ipv4}/32'
                        #### Remove Primary IPv4 on other device
                        other_device = Device.objects.annotate(
                            primary_ip4_host_str=Func(F('primary_ip4__host'), Value('escape'), function='encode', output_field=models.CharField())
                        ).filter(
                            primary_ip4_host_str=obj.ipv4
                        ).first()
                        
                        if other_device:
                            other_device.primary_ip4 = None
                            other_device.save()

                        interface = Interface.objects.filter(device=device)
                        if interface:
                            interface = interface.first()
                        else:
                            interface = Interface.objects.create(name='management1', device=device, type='other')

                        ipaddress = IPAddress.objects.filter(address=address)
                        if ipaddress:
                            ipaddress = ipaddress.first()
                        else:
                            prefix = Prefix.objects.get_or_create(prefix=address, defaults={'status':status_active_for_prefix()})
                            ipaddress = IPAddress.objects.create(address=address, status=status_active_for_ipaddress())
                        
                        ipaddress.assigned_object = interface
                        ipaddress.save()
                        device.primary_ip4 = ipaddress
                        device.save()

                    log_message = f"Conflicted device resolved - {obj.hostname} successfully updated."
                    
                msg = f'Conflicts successfully resolved.'
                messages.success(self.request, msg)

                return redirect(self.get_return_url(request))
                
        initial_data = {'pk': pk_list, 'device_types': device_types, 'locations': locations}
        for k, v in get_default_objects().items():
            if v:
                initial_data.setdefault(k, str(v.id))
        initial_data.setdefault('status', status_active())

        if request.POST.get('_all'):
            initial_data['_all'] = 'on'

        if len(device_types) > 1:
            initial_data['device_type'] = 'keep_original'
        if len(device_types) == 1 and (dt := DeviceType.objects.filter(model__iexact=device_types[0][0]).first()):
            initial_data['device_type'] = dt.id

        if len(locations) > 1:
            initial_data['location'] = 'keep_original'
        
        if len(locations) == 1 and (location := Location.objects.filter(name=locations[0][0]).first()):
            initial_data['location'] = location.id

        form = create_form(self.form, None, models.SlurpitImportedDevice, initial_data)
        restrict_form_fields(form, request.user)
                
        # Retrieve objects being edited
        table = self.table(self.queryset.filter(mapped_device_id__isnull=True), orderable=False)
        if not table.rows:
            messages.warning(request, "No {} were selected.".format(model._meta.verbose_name_plural))
            log_message = "Failed to onboard since no devices were selected."
            
            return redirect(self.get_return_url(request))

        return render(request, self.template_name, {
            'model': model,
            'form': form,
            'table': table,
            'obj_type_plural': self.queryset.model._meta.verbose_name_plural,
            'return_url': self.get_return_url(request),
            **self.slurpit_data
        })

    def _update_objects(self, form, request):
        device_type = None
        if form.cleaned_data['device_type'] != 'keep_original':
            device_type = DeviceType.objects.filter(id=form.cleaned_data['device_type']).first()

        location = None
        if form.cleaned_data['location'] != 'keep_original':
            location = Location.objects.filter(id=form.cleaned_data['location']).first()
        updated_objects = []
        data = get_form_device_data(form)

        objs = self.queryset.filter(pk__in=form.cleaned_data['pk'])
        
        for obj in objs:
            if obj.mapped_device_id is not None:
                continue

            dt = device_type
            if not device_type:
                dt = obj.mapped_devicetype
            
            item_location = location
            if not item_location:
                if obj.location is None or obj.location == "":
                    defaults = get_default_objects()
                    item_location = defaults['location']

                    if not item_location:
                        add_default_mandatory_objects()
                        defaults = get_default_objects()
                        item_location = defaults['location']
                else:
                    item_location = Location.objects.get(name=obj.location)

            try:
                device = get_dcim_device(obj, device_type=dt, location=item_location, **data)
                obj.mapped_device = device
                obj.save()
                updated_objects.append(obj)
            except Exception as e:
                return [], "fail", str(e), obj.hostname

            
            # Take a snapshot of change-logged models
            if hasattr(device, 'snapshot'):
                device.snapshot()
            
            if form.cleaned_data.get('add_tags', None):
                device.tags.add(*form.cleaned_data['add_tags'])
            if form.cleaned_data.get('remove_tags', None):
                device.tags.remove(*form.cleaned_data['remove_tags'])

        return updated_objects, "success", "", ""


@method_decorator(slurpit_plugin_registered, name='dispatch')
class ImportDevices(View):
    def get(self, request, *args, **kwargs):
        offset = request.GET.get("offset", None)
        try:
            if offset is not None:
                offset = int(offset)
                if offset == 0:
                    sync_locations()
                    start_device_import()
                devices, log_message = get_devices(offset)
                if devices is not None and len(devices) > 0:
                    import_devices(devices)
                    offset += len(devices)

                if devices is None:
                    messages.error(request, "Please confirm the Slurp'it server is running and reachable.")
                    return JsonResponse({"action": "error", "error": "ERROR"})

                return JsonResponse({"action": "import", "offset": offset})
            
            process_import()
            messages.info(request, "Synced the devices from Slurp'it.")
            return JsonResponse({"action": "process"})
        except requests.exceptions.RequestException as e:
            messages.error(request, "An error occured during querying Slurp'it!")
            
        return JsonResponse({"action": "", "error": "ERROR"})
    

