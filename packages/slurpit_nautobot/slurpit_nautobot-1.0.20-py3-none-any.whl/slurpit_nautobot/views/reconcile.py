from nautobot.core.views import generic

from ..models import (
    SlurpitImportedDevice, SlurpitIPAddress, SlurpitInterface, SlurpitPrefix
)
from .. import forms, importer, models, tables
from ..decorators import slurpit_plugin_registered
from django.utils.decorators import method_decorator
from ..references.generic import SlurpitViewMixim
from django.contrib import messages
from urllib.parse import urlencode
from ..management.choices import *
from django.shortcuts import redirect
from django.urls import reverse
from ..importer import BATCH_SIZE
from django.db import transaction
from nautobot.ipam.models import VRF, IPAddress, Prefix, VRFPrefixAssignment
from nautobot.dcim.models import Interface
from nautobot.extras.models import Status
from django.shortcuts import render
from nautobot.core.utils.data import shallow_compare_dict
from django.http import JsonResponse

from ..filtersets import (
    SlurpitPrefixFilterSet, SlurpitInterfaceFilterSet, SlurpitIPAddressFilterSet
)
from ..forms import (
    SlurpitPrefixForm, 
    SlurpitInterfaceForm, 
    SlurpitIPAddressForm, 
    SlurpitPrefixEditForm, 
    SlurpitInterfaceEditForm, 
    SlurpitIPAddressEditForm
)

@method_decorator(slurpit_plugin_registered, name='dispatch')
class ReconcileView(SlurpitViewMixim, generic.ObjectListView):
    queryset = models.SlurpitIPAddress.objects.exclude(host=None)
    table = tables.SlurpitIPAddressTable
    template_name = "slurpit_nautobot/reconcile.html"
    action_buttons = []
    filterset = SlurpitIPAddressFilterSet

    def get(self, request, *args, **kwargs):
        
        tab = request.GET.get('tab')
        if tab == None or tab == 'ipam':
            self.queryset = SlurpitIPAddress.objects.exclude(host=None)
            self.table = tables.SlurpitIPAddressTable
            self.filterset = SlurpitIPAddressFilterSet
        elif tab == 'prefix':
            self.queryset = models.SlurpitPrefix.objects.exclude(network=None)
            self.table = tables.SlurpitPrefixTable
            self.filterset = SlurpitPrefixFilterSet
        else:
            self.queryset = models.SlurpitInterface.objects.exclude(name='')
            self.table = tables.SlurpitInterfaceTable
            self.filterset = SlurpitInterfaceFilterSet

        return super().get(request, *args, **kwargs)
    
    def slurpit_extra_context(self):
        reconcile_type = self.request.GET.get('tab')
        pk = self.request.GET.get('pk')
        return_values = {}
        """
        GET handler for rendering child objects.
        """
        title = ""
        instance = None
        diff_added = None
        diff_removed = None    
        action = 'Updated'

        if pk:
            if reconcile_type == 'interface':
                incomming_queryset = SlurpitInterface.objects.filter(pk=pk).first()
                name = incomming_queryset.name
                device = incomming_queryset.device

                incomming_change = {
                    'name': name,
                    'status': str(incomming_queryset.status),
                    'label': incomming_queryset.label,
                    'device': str(incomming_queryset.device),
                    'type': incomming_queryset.type,
                    'vrf': str(incomming_queryset.vrf),
                    'mode': str(incomming_queryset.mode),
                    'description': incomming_queryset.description
                }

                title = str(name)
                updated_time = incomming_queryset.last_updated

                current_queryset = Interface.objects.filter(name=name, device=device)

                if current_queryset:
                    instance = current_queryset.first() 
                    current_state = {
                        'name': str(instance.name),
                        'status': str(instance.status),
                        'label': str(instance.label),
                        'device': str(instance.device),
                        'type': str(instance.type),
                        'vrf': str(instance.vrf),
                        'mode': str(instance.mode),
                        'description': instance.description
                    }
                    
                else:
                    current_state = None
                    instance = None
                    action = 'Created'
                

                if current_state and incomming_change:
                    diff_added = shallow_compare_dict(
                        current_state or dict(),
                        incomming_change or dict(),
                        exclude=['last_updated'],
                    )
                    diff_removed = {
                        x: current_state.get(x) for x in diff_added
                    } if current_state else {}
                else:
                    diff_added = None
                    diff_removed = None

                object_type = f'{Interface._meta.app_label} | {Interface._meta.verbose_name}'
            
            elif reconcile_type == 'prefix':
                incomming_queryset = SlurpitPrefix.objects.filter(pk=pk).first()
                prefix = incomming_queryset.prefix
                namespace = incomming_queryset.namespace

                incomming_change = {
                    'prefix': str(incomming_queryset.prefix),
                    'status': str(incomming_queryset.status),
                    'namespace': str(incomming_queryset.namespace),
                    'type': incomming_queryset.type,
                    'role': str(incomming_queryset.role),
                    'tenant': str(incomming_queryset.tenant),
                    'description': incomming_queryset.description
                }
                title = str(prefix)
                updated_time = incomming_queryset.last_updated

                temp = Prefix(prefix=prefix, namespace=namespace, status=incomming_queryset.status)
                current_queryset = Prefix.objects.filter(network=temp.network, prefix_length=temp.prefix_length, namespace=namespace)

                if current_queryset:
                    instance = current_queryset.first() 
                    current_state = {
                        'prefix': str(instance.prefix),
                        'status': str(instance.status),
                        'namespace': str(instance.namespace),
                        'type': instance.type,
                        'role': str(instance.role),
                        'tenant': str(instance.tenant),
                        'description': instance.description
                    }
                    
                else:
                    current_state = None
                    instance = None
                    action = 'Created'
                

                if current_state and incomming_change:
                    diff_added = shallow_compare_dict(
                        current_state or dict(),
                        incomming_change or dict(),
                        exclude=['last_updated'],
                    )
                    diff_removed = {
                        x: current_state.get(x) for x in diff_added
                    } if current_state else {}
                else:
                    diff_added = None
                    diff_removed = None

                object_type = f'{Prefix._meta.app_label} | {Prefix._meta.verbose_name}'
            else:
                incomming_queryset = SlurpitIPAddress.objects.filter(pk=pk).first()
                address = incomming_queryset.address
                namespace = incomming_queryset.namespace

                incomming_change = {
                    'address': str(incomming_queryset.address),
                    'status': str(incomming_queryset.status),
                    'namespace': str(incomming_queryset.namespace),
                    'type': incomming_queryset.type,
                    'role': str(incomming_queryset.role),
                    'dns_name': incomming_queryset.dns_name,
                    'tenant': incomming_queryset.tenant,
                    'description': incomming_queryset.description
                }
                title = str(address)
                updated_time = incomming_queryset.last_updated

                current_queryset = IPAddress.objects.filter(address=address, parent__namespace=namespace)

                if current_queryset:
                    instance = current_queryset.first() 
                    current_state = {
                        'address': str(instance.address),
                        'status': str(instance.status),
                        'namespace': str(instance.parent.namespace),
                        'type': instance.type,
                        'role': str(instance.role),
                        'dns_name': instance.dns_name,
                        'tenant': instance.tenant,
                        'description': instance.description
                    }
                    
                else:
                    current_state = None
                    instance = None
                    action = 'Created'
                

                if current_state and incomming_change:
                    diff_added = shallow_compare_dict(
                        current_state or dict(),
                        incomming_change or dict(),
                        exclude=['last_updated'],
                    )
                    diff_removed = {
                        x: current_state.get(x) for x in diff_added
                    } if current_state else {}
                else:
                    diff_added = None
                    diff_removed = None

                object_type = f'{IPAddress._meta.app_label} | {IPAddress._meta.verbose_name}'
            
            return_values = {
                'object': instance,
                'title': title,
                'diff_added': diff_added,
                'diff_removed': diff_removed,
                'incomming_change': incomming_change,
                'current_state': current_state,
                'updated_time': updated_time,
                'action': action,
                'object_type': object_type
            }

        if reconcile_type == 'interface':
            edit_bulk_url = reverse("plugins:slurpit_nautobot:slurpitinterface_bulk_edit")
        elif reconcile_type == 'prefix':
            edit_bulk_url = reverse("plugins:slurpit_nautobot:slurpitprefix_bulk_edit")
        else:
            edit_bulk_url = reverse("plugins:slurpit_nautobot:slurpitipaddress_bulk_edit")

        return_values = {
            **return_values,
            'ipam_count': models.SlurpitIPAddress.objects.exclude(host = None).count(),
            'interface_count': models.SlurpitInterface.objects.exclude(name = '').count(),
            'prefix_count': models.SlurpitPrefix.objects.exclude(network = None).count(),
            'edit_bulk_url': edit_bulk_url,
            **self.slurpit_data
        }


        return return_values

    def post(self, request, **kwargs):
        pk_list = request.POST.getlist('pk')
        action = request.POST.get('action')
        tab = request.POST.get('tab')
        _all = request.POST.get('_all')

        if action == 'get':
            pk = request.POST.get('pk')

            title = ""
            instance = None
            diff_added = None
            diff_removed = None    
            action = 'Updated'
            if tab == 'interface':
                incomming_queryset = SlurpitInterface.objects.filter(pk=pk).first()
                name = incomming_queryset.name
                device = incomming_queryset.device

                incomming_change = {
                    'name': name,
                    'status': str(incomming_queryset.status),
                    'label': incomming_queryset.label,
                    'device': str(incomming_queryset.device),
                    'type': incomming_queryset.type,
                    'vrf': str(incomming_queryset.vrf),
                    'mode': str(incomming_queryset.mode),
                    'enabled': str(incomming_queryset.enabled),
                    'description': incomming_queryset.description
                }

                title = str(name)
                updated_time = incomming_queryset.last_updated

                current_queryset = Interface.objects.filter(name=name, device=device)

                if current_queryset:
                    instance = current_queryset.first() 
                    current_state = {
                        'name': str(instance.name),
                        'status': str(instance.status),
                        'label': str(instance.label),
                        'device': str(instance.device),
                        'type': str(instance.type),
                        'vrf': str(instance.vrf),
                        'mode': str(instance.mode),
                        'enabled': str(instance.enabled),
                        'description': instance.description
                    }
                    
                else:
                    current_state = None
                    instance = None
                    action = 'Created'
                

                if current_state and incomming_change:
                    diff_added = shallow_compare_dict(
                        current_state or dict(),
                        incomming_change or dict(),
                        exclude=['last_updated'],
                    )
                    diff_removed = {
                        x: current_state.get(x) for x in diff_added
                    } if current_state else {}
                else:
                    diff_added = None
                    diff_removed = None

                object_type = f'{Interface._meta.app_label} | {Interface._meta.verbose_name}'
            
            elif tab == 'prefix':
                incomming_queryset = SlurpitPrefix.objects.filter(pk=pk).first()
                prefix = incomming_queryset.prefix
                namespace = incomming_queryset.namespace

                incomming_change = {
                    'prefix': str(incomming_queryset.prefix),
                    'status': str(incomming_queryset.status),
                    'namespace': str(incomming_queryset.namespace),
                    'type': incomming_queryset.type,
                    'role': str(incomming_queryset.role),
                    'vrf': str(incomming_queryset.vrf),
                    'tenant': str(incomming_queryset.tenant),
                    'description': incomming_queryset.description
                }
                title = str(prefix)
                updated_time = incomming_queryset.last_updated

                temp = Prefix(prefix=prefix, namespace=namespace, status=incomming_queryset.status)
                current_queryset = Prefix.objects.filter(network=temp.network, prefix_length=temp.prefix_length, namespace=namespace)

                if current_queryset:
                    instance = current_queryset.first() 

                    vrf_names = VRFPrefixAssignment.objects.filter(prefix=instance).values_list('vrf__name', flat=True)
                    joined_vrf_names = ', '.join(vrf_names)

                    current_state = {
                        'prefix': str(instance.prefix),
                        'status': str(instance.status),
                        'namespace': str(instance.namespace),
                        'type': instance.type,
                        'role': str(instance.role),
                        'vrf': joined_vrf_names,
                        'tenant': str(instance.tenant),
                        'description': instance.description
                    }
                    
                else:
                    current_state = None
                    instance = None
                    action = 'Created'
                

                if current_state and incomming_change:
                    diff_added = shallow_compare_dict(
                        current_state or dict(),
                        incomming_change or dict(),
                        exclude=['last_updated'],
                    )
                    diff_removed = {
                        x: current_state.get(x) for x in diff_added
                    } if current_state else {}
                else:
                    diff_added = None
                    diff_removed = None

                object_type = f'{Prefix._meta.app_label} | {Prefix._meta.verbose_name}'
            else:
                incomming_queryset = SlurpitIPAddress.objects.filter(pk=pk).first()
                address = incomming_queryset.address
                namespace = incomming_queryset.namespace

                incomming_change = {
                    'address': str(incomming_queryset.address),
                    'status': str(incomming_queryset.status),
                    'namespace': str(incomming_queryset.namespace),
                    'type': incomming_queryset.type,
                    'role': str(incomming_queryset.role),
                    'dns_name': incomming_queryset.dns_name,
                    'tenant': incomming_queryset.tenant,
                    'description': incomming_queryset.description
                }
                title = str(address)
                updated_time = incomming_queryset.last_updated

                current_queryset = IPAddress.objects.filter(address=address, parent__namespace=namespace)

                if current_queryset:
                    instance = current_queryset.first() 
                    current_state = {
                        'address': str(instance.address),
                        'status': str(instance.status),
                        'namespace': str(instance.parent.namespace),
                        'type': instance.type,
                        'role': str(instance.role),
                        'dns_name': instance.dns_name,
                        'tenant': instance.tenant,
                        'description': instance.description
                    }
                    
                else:
                    current_state = None
                    instance = None
                    action = 'Created'
                

                if current_state and incomming_change:
                    diff_added = shallow_compare_dict(
                        current_state or dict(),
                        incomming_change or dict(),
                        exclude=['last_updated'],
                    )
                    diff_removed = {
                        x: current_state.get(x) for x in diff_added
                    } if current_state else {}
                else:
                    diff_added = None
                    diff_removed = None

                object_type = f'{IPAddress._meta.app_label} | {IPAddress._meta.verbose_name}'

            return_values = {
                # 'object': instance,
                'title': title,
                'diff_added': diff_added,
                'diff_removed': diff_removed,
                'incomming_change': incomming_change,
                'current_state': current_state,
                'updated_time': updated_time,
                'action': action,
                'object_type': object_type
            }

            return JsonResponse(return_values)


        if _all or len(pk_list):
            if action == 'decline':
                try:
                    if tab == 'interface':
                        if _all:
                            deline_items = models.SlurpitInterface.objects.exclude(name='').delete()
                        else:
                            deline_items = models.SlurpitInterface.objects.filter(pk__in=pk_list).delete()

                        messages.info(request, "Declined the selected Interfaces successfully .")
                    elif tab == 'prefix':
                        if _all:
                            deline_items = models.SlurpitPrefix.objects.exclude(network=None).delete()
                        else:
                            deline_items = models.SlurpitPrefix.objects.filter(pk__in=pk_list).delete()
                        messages.info(request, "Declined the selected Prefixes successfully .")
                    else:
                        if _all:
                            deline_items = models.SlurpitIPAddress.objects.exclude(host=None).delete()
                        else:
                            deline_items = models.SlurpitIPAddress.objects.filter(pk__in=pk_list).delete()
                        messages.info(request, "Declined the selected IP Addresses successfully .")
                except:
                    if tab == 'interface':
                        messages.warning(request, "Failed to decline Interfaces.")
                    elif tab == 'prefix':
                        messages.warning(request, "Failed to decline Prefixes.")
                    else:
                        messages.warning(request, "Failed to decline IP Addresses.")
            else:
                batch_insert_qs = []
                batch_update_qs = []
                batch_insert_ids = []
                batch_update_ids = []
                
                if tab == 'interface':
                    if _all:
                        reconcile_items = SlurpitInterface.objects.exclude(name='')
                    else:
                        reconcile_items = SlurpitInterface.objects.filter(pk__in=pk_list)

                    initial_obj = SlurpitInterface.objects.filter(name='').values(
                        'ignore_status',
                        'ignore_label',
                        'ignore_type',
                        'ignore_vrf',
                        'ignore_description',
                        'ignore_mode'
                    ).first()
                    initial_interface_values = {}
                    interface_update_ignore_values = []

                    if initial_obj:
                        initial_interface_values = {**initial_obj}

                        for key in initial_interface_values.keys():
                            if initial_interface_values[key]:
                                interface_update_ignore_values.append(key)

                    updated_fields = [
                        'status', 
                        'label', 
                        'type', 
                        'vrf', 
                        'mode', 
                        'description',
                        'enabled'
                    ]
                    fields_to_remove = []
                    
                    for field in updated_fields:
                        ignore_field = f'ignore_{field}'
                        if ignore_field in interface_update_ignore_values:
                            fields_to_remove.append(field)

                    updated_fields = list(set(updated_fields) - set(fields_to_remove))


                    for item in reconcile_items:
                        nautobot_interface = Interface.objects.filter(name=item.name, device=item.device)
                        # If the interface is existed in nautobot
                        if nautobot_interface:
                            nautobot_interface = nautobot_interface.first()

                            for field in item._meta.fields:
                                field_name = field.name
                                field_value = getattr(item, field_name)
                                if field_name in updated_fields and field_value is not None and field_value != "":
                                    setattr(nautobot_interface, field_name, field_value)


                            batch_update_qs.append(nautobot_interface)
                            batch_update_ids.append(item.pk)
                        else:
                            batch_insert_qs.append(
                                Interface(
                                    name = item.name,
                                    status = item.status, 
                                    device = item.device,
                                    label = item. label, 
                                    type = item.type,
                                    description = item.description,
                                    mode = item.mode,
                                    vrf = item.vrf,
                                    enabled = item.enabled
                            ))
                            batch_insert_ids.append(item.pk)
                        
                    count = len(batch_insert_qs)
                    offset = 0
                    while offset < count:
                        batch_qs = batch_insert_qs[offset:offset + BATCH_SIZE]
                        batch_ids = batch_insert_ids[offset:offset + BATCH_SIZE]
                        to_import = []        
                        for interface_item in batch_qs:
                            to_import.append(interface_item)

                        with transaction.atomic():
                            Interface.objects.bulk_create(to_import)
                            SlurpitInterface.objects.filter(pk__in=batch_ids).delete()
                        offset += BATCH_SIZE

                    count = len(batch_update_qs)
                    offset = 0
                    while offset < count:
                        batch_qs = batch_update_qs[offset:offset + BATCH_SIZE]
                        batch_ids = batch_update_ids[offset:offset + BATCH_SIZE]
                        to_import = []        
                        for interface_item in batch_qs:
                            to_import.append(interface_item)

                        with transaction.atomic():
                            Interface.objects.bulk_update(to_import, fields=updated_fields)
                        
                            SlurpitInterface.objects.filter(pk__in=batch_ids).delete()

                        offset += BATCH_SIZE
                elif tab == 'prefix':
                    if _all:
                        reconcile_items =SlurpitPrefix.objects.exclude(network=None)
                    else:
                        reconcile_items =SlurpitPrefix.objects.filter(pk__in=pk_list)

                    initial_obj = SlurpitPrefix.objects.filter(network=None).values(
                        'ignore_status',
                        'ignore_type',
                        'ignore_role',
                        'ignore_tenant',
                        'ignore_description'
                    ).first()
                    initial_prefix_values = {}
                    prefix_update_ignore_values = []

                    if initial_obj:
                        initial_prefix_values = {**initial_obj}

                        for key in initial_prefix_values.keys():
                            if initial_prefix_values[key]:
                                prefix_update_ignore_values.append(key)

                    updated_fields = [
                        'status', 
                        'type', 
                        'role', 
                        'tenant', 
                        'description'
                    ]
                    fields_to_remove = []
                    
                    for field in updated_fields:
                        ignore_field = f'ignore_{field}'
                        if ignore_field in prefix_update_ignore_values:
                            fields_to_remove.append(field)

                    updated_fields = list(set(updated_fields) - set(fields_to_remove))

                    for item in reconcile_items:
                        temp = Prefix(prefix=item.prefix, namespace=item.namespace, status=item.status)

                        nautobot_prefix = Prefix.objects.filter(network=temp.network, prefix_length=temp.prefix_length, namespace=item.namespace)
                        # If the ip address is existed in nautobot
                        if nautobot_prefix:
                            nautobot_prefix = nautobot_prefix.first()

                            for field in item._meta.fields:
                                field_name = field.name
                                field_value = getattr(item, field_name)
                                if field_name in updated_fields and field_value is not None and field_value != "":
                                    setattr(nautobot_prefix, field_name, field_value)

                            if item.description is None:
                                nautobot_prefix.description = ""

                            batch_update_qs.append(nautobot_prefix)
                            batch_update_ids.append(item.pk)
                        else:
                            prefix_item = {
                                'prefix':item.prefix, 
                                'namespace':item.namespace,
                                'status' : item. status, 
                                'role' : item.role,
                                'description' : item.description,
                                'tenant' : item.tenant,
                                'type' : item.type
                            }
                            nautobot_item = Prefix(**prefix_item)
                            
                            batch_insert_qs.append(
                                nautobot_item
                            )

                            batch_insert_ids.append(item.pk)
                        
                    count = len(batch_insert_qs)
                    offset = 0
                    while offset < count:
                        batch_qs = batch_insert_qs[offset:offset + BATCH_SIZE]
                        batch_ids = batch_insert_ids[offset:offset + BATCH_SIZE]
                        to_import = []        
                        for prefix_item in batch_qs:
                            to_import.append(prefix_item)

                        with transaction.atomic():
                            Prefix.objects.bulk_create(to_import)

                            # Update VRF
                            for sp_pk in batch_ids:
                                slurpit_prefix_item = SlurpitPrefix.objects.filter(pk=sp_pk).first()

                                temp = Prefix(
                                    prefix=slurpit_prefix_item.prefix, 
                                    namespace=slurpit_prefix_item.namespace, 
                                    status=slurpit_prefix_item.status)
                            
                                nautobot_prefix = Prefix.objects.filter(
                                    network=temp.network, 
                                    prefix_length=temp.prefix_length, 
                                    namespace=slurpit_prefix_item.namespace).first()
        
                                # Update VRF
                                if nautobot_prefix:
                                    VRFPrefixAssignment.objects.filter(
                                        prefix=nautobot_prefix
                                    ).delete()

                                    if slurpit_prefix_item.vrf != "":
                                    
                                        new_vrf = VRF.objects.filter(
                                            name = slurpit_prefix_item.vrf,
                                            namespace=slurpit_prefix_item.namespace
                                        ).first()

                                        if new_vrf is None:
                                            new_vrf = VRF.objects.create(
                                                name = slurpit_prefix_item.vrf,
                                                namespace=slurpit_prefix_item.namespace
                                            )
                                    
                                        new_vrf.prefixes.add(nautobot_prefix)

                            SlurpitPrefix.objects.filter(pk__in=batch_ids).delete()
                        
                        offset += BATCH_SIZE

                    count = len(batch_update_qs)
                    offset = 0
                    while offset < count:
                        batch_qs = batch_update_qs[offset:offset + BATCH_SIZE]
                        batch_ids = batch_update_ids[offset:offset + BATCH_SIZE]
                        to_import = []        
                        for prefix_item in batch_qs:
                            to_import.append(prefix_item)

                        with transaction.atomic():
                            Prefix.objects.bulk_update(to_import, fields=updated_fields)

                            # Update VRF
                            for sp_pk in batch_ids:
                                slurpit_prefix_item = SlurpitPrefix.objects.filter(pk=sp_pk).first()

                                temp = Prefix(
                                    prefix=slurpit_prefix_item.prefix, 
                                    namespace=slurpit_prefix_item.namespace, 
                                    status=slurpit_prefix_item.status)
                            
                                nautobot_prefix = Prefix.objects.filter(
                                    network=temp.network, 
                                    prefix_length=temp.prefix_length, 
                                    namespace=slurpit_prefix_item.namespace).first()
        
                                # Update VRF
                                if nautobot_prefix:
                                    VRFPrefixAssignment.objects.filter(
                                        prefix=nautobot_prefix
                                    ).delete()

                                    if slurpit_prefix_item.vrf != "":
                                    
                                        new_vrf = VRF.objects.filter(
                                            name = slurpit_prefix_item.vrf,
                                            namespace=slurpit_prefix_item.namespace
                                        ).first()

                                        if new_vrf is None:
                                            new_vrf = VRF.objects.create(
                                                name = slurpit_prefix_item.vrf,
                                                namespace=slurpit_prefix_item.namespace
                                            )
                                    
                                        new_vrf.prefixes.add(nautobot_prefix)
                                        
                            SlurpitPrefix.objects.filter(pk__in=batch_ids).delete()

                        offset += BATCH_SIZE
                else:
                    if _all:
                        reconcile_items =SlurpitIPAddress.objects.exclude(host=None)
                    else:
                        reconcile_items =SlurpitIPAddress.objects.filter(pk__in=pk_list)
                    
                    initial_obj = SlurpitIPAddress.objects.filter(host=None).values(
                        'ignore_status', 
                        'ignore_type', 
                        'ignore_role', 
                        'ignore_tenant', 
                        'ignore_description',
                        'ignore_dns_name'
                    ).first()

                    initial_ipaddress_values = {}
                    ipaddress_update_ignore_values = []

                    if initial_obj:
                        initial_ipaddress_values = {**initial_obj}

                        for key in initial_ipaddress_values.keys():
                            if initial_ipaddress_values[key]:
                                ipaddress_update_ignore_values.append(key)

                    updated_fields = [
                        'status', 
                        'type', 
                        'role', 
                        'tenant',
                        'description',
                        'dns_name'
                    ]
                    fields_to_remove = []
                    
                    for field in updated_fields:
                        ignore_field = f'ignore_{field}'
                        if ignore_field in ipaddress_update_ignore_values:
                            fields_to_remove.append(field)


                    updated_fields = list(set(updated_fields) - set(fields_to_remove))

                    for item in reconcile_items:
                        nautobot_ipaddress = IPAddress.objects.filter(address=item.address, parent__namespace=item.namespace)
                        # If the ip address is existed in nautobot
                        if nautobot_ipaddress:
                            nautobot_ipaddress = nautobot_ipaddress.first()
                            for field in item._meta.fields:
                                field_name = field.name
                                field_value = getattr(item, field_name)
                                if field_name in updated_fields and field_value is not None and field_value != "":
                                    setattr(nautobot_ipaddress, field_name, field_value)


                            if item.dns_name is None:
                                nautobot_ipaddress.dns_name = ""

                            if item.description is None:
                                nautobot_ipaddress.description = ""

                            batch_update_qs.append(nautobot_ipaddress)
                            batch_update_ids.append(item.pk)
                        else:
                            ipaddress_item = {
                                'address':item.address, 
                                'type':item.type,
                                'status' : item. status, 
                                'role' : item.role,
                                'description' : item.description,
                                'tenant' : item.tenant,
                                'dns_name' : item.dns_name,
                                'namespace' : item.namespace
                            }
                            nautobot_item = IPAddress(**ipaddress_item)
                            parent = None
                            try:
                                parent = nautobot_item._get_closest_parent()
                            except:
                                parent = None

                            if parent is None:
                                status = Status.objects.get(name='Active')
                                parent = Prefix.objects.create(prefix=f'{nautobot_item.host}/32', namespace=ipaddress_item['namespace'], status=status)
                            ipaddress_item['parent'] = parent

                            batch_insert_qs.append(
                                IPAddress(
                                    **ipaddress_item
                                )
                            )

                            batch_insert_ids.append(item.pk)
                        
                    count = len(batch_insert_qs)
                    offset = 0
                    while offset < count:
                        batch_qs = batch_insert_qs[offset:offset + BATCH_SIZE]
                        batch_ids = batch_insert_ids[offset:offset + BATCH_SIZE]
                        to_import = []        
                        for ipaddress_item in batch_qs:
                            to_import.append(ipaddress_item)

                        with transaction.atomic():
                            IPAddress.objects.bulk_create(to_import)

                            SlurpitIPAddress.objects.filter(pk__in=batch_ids).delete()
                        offset += BATCH_SIZE

                    count = len(batch_update_qs)
                    offset = 0
                    while offset < count:
                        batch_qs = batch_update_qs[offset:offset + BATCH_SIZE]
                        batch_ids = batch_update_ids[offset:offset + BATCH_SIZE]
                        to_import = []        
                        for ipaddress_item in batch_qs:
                            to_import.append(ipaddress_item)

                        with transaction.atomic():
                            IPAddress.objects.bulk_update(to_import, fields=updated_fields)
                        
                            SlurpitIPAddress.objects.filter(pk__in=batch_ids).delete()

                        offset += BATCH_SIZE
        else:
            messages.warning(request, "No Reconcile Items were selected.")

            if action == 'accept':
                if tab == 'interface':
                    log_message = "Failed to accept since no ip addresses were selected."
                elif tab == 'prefix':
                    log_message = "Failed to accept since no prefixes were selected."
                else:
                    log_message = "Failed to accept since no interfaces were selected."
            else:
                if tab == 'interface':
                    log_message = "Failed to decline since no ip addresses were selected."
                elif tab == 'prefix':
                    log_message = "Failed to decline since no prefixes were selected."
                
                else:
                    log_message = "Failed to decline since no interfaces were selected."
        
        if tab is None or tab == '':
            tab = 'ipam'
        query_params = {'tab': tab}
        base_url = reverse("plugins:slurpit_nautobot:reconcile_list")
        # Encode your query parameters and append them to the base URL
        url_with_querystring = f"{base_url}?{urlencode(query_params)}"

        return redirect(url_with_querystring)

class ReconcileDetailView(generic.ObjectView):
    queryset = models.SlurpitIPAddress.objects.all()

    template_name = 'slurpit_nautobot/reconcile_detail.html'

    def get(self, request, pk, reconcile_type, **kwargs):
        """
        GET handler for rendering child objects.
        """
        title = ""
        instance = None
        diff_added = None
        diff_removed = None    
        action = 'Updated'
        if reconcile_type == 'interface':
            incomming_queryset = SlurpitInterface.objects.filter(pk=pk).first()
            name = incomming_queryset.name
            device = incomming_queryset.device

            incomming_change = {
                'name': name,
                'status': str(incomming_queryset.status),
                'label': incomming_queryset.label,
                'device': str(incomming_queryset.device),
                'type': incomming_queryset.type,
                'vrf': str(incomming_queryset.vrf),
                'mode': str(incomming_queryset.mode),
                'description': incomming_queryset.description
            }

            title = str(name)
            updated_time = incomming_queryset.last_updated

            current_queryset = Interface.objects.filter(name=name, device=device)

            if current_queryset:
                instance = current_queryset.first() 
                current_state = {
                    'name': str(instance.name),
                    'status': str(instance.status),
                    'label': str(instance.label),
                    'device': str(instance.device),
                    'type': str(instance.type),
                    'vrf': str(instance.vrf),
                    'mode': str(instance.mode),
                    'description': instance.description
                }
                
            else:
                current_state = None
                instance = None
                action = 'Created'
            

            if current_state and incomming_change:
                diff_added = shallow_compare_dict(
                    current_state or dict(),
                    incomming_change or dict(),
                    exclude=['last_updated'],
                )
                diff_removed = {
                    x: current_state.get(x) for x in diff_added
                } if current_state else {}
            else:
                diff_added = None
                diff_removed = None

            object_type = f'{Interface._meta.app_label} | {Interface._meta.verbose_name}'
        
        elif reconcile_type == 'prefix':
            incomming_queryset = SlurpitPrefix.objects.filter(pk=pk).first()
            prefix = incomming_queryset.prefix
            namespace = incomming_queryset.namespace

            incomming_change = {
                'prefix': str(incomming_queryset.prefix),
                'status': str(incomming_queryset.status),
                'namespace': str(incomming_queryset.namespace),
                'type': incomming_queryset.type,
                'role': str(incomming_queryset.role),
                'tenant': str(incomming_queryset.tenant),
                'description': incomming_queryset.description
            }
            title = str(prefix)
            updated_time = incomming_queryset.last_updated

            temp = Prefix(prefix=prefix, namespace=namespace, status=incomming_queryset.status)
            current_queryset = Prefix.objects.filter(network=temp.network, prefix_length=temp.prefix_length, namespace=namespace)

            if current_queryset:
                instance = current_queryset.first() 
                current_state = {
                    'prefix': str(instance.prefix),
                    'status': str(instance.status),
                    'namespace': str(instance.namespace),
                    'type': instance.type,
                    'role': str(instance.role),
                    'tenant': str(instance.tenant),
                    'description': instance.description
                }
                
            else:
                current_state = None
                instance = None
                action = 'Created'
            

            if current_state and incomming_change:
                diff_added = shallow_compare_dict(
                    current_state or dict(),
                    incomming_change or dict(),
                    exclude=['last_updated'],
                )
                diff_removed = {
                    x: current_state.get(x) for x in diff_added
                } if current_state else {}
            else:
                diff_added = None
                diff_removed = None

            object_type = f'{Prefix._meta.app_label} | {Prefix._meta.verbose_name}'
        else:
            incomming_queryset = SlurpitIPAddress.objects.filter(pk=pk).first()
            address = incomming_queryset.address
            namespace = incomming_queryset.namespace

            incomming_change = {
                'address': str(incomming_queryset.address),
                'status': str(incomming_queryset.status),
                'namespace': str(incomming_queryset.namespace),
                'type': incomming_queryset.type,
                'role': str(incomming_queryset.role),
                'dns_name': incomming_queryset.dns_name,
                'tenant': incomming_queryset.tenant,
                'description': incomming_queryset.description
            }
            title = str(address)
            updated_time = incomming_queryset.last_updated

            current_queryset = IPAddress.objects.filter(address=address, parent__namespace=namespace)

            if current_queryset:
                instance = current_queryset.first() 
                current_state = {
                    'address': str(instance.address),
                    'status': str(instance.status),
                    'namespace': str(instance.parent.namespace),
                    'type': instance.type,
                    'role': str(instance.role),
                    'dns_name': instance.dns_name,
                    'tenant': instance.tenant,
                    'description': instance.description
                }
                
            else:
                current_state = None
                instance = None
                action = 'Created'
            

            if current_state and incomming_change:
                diff_added = shallow_compare_dict(
                    current_state or dict(),
                    incomming_change or dict(),
                    exclude=['last_updated'],
                )
                diff_removed = {
                    x: current_state.get(x) for x in diff_added
                } if current_state else {}
            else:
                diff_added = None
                diff_removed = None

            object_type = f'{IPAddress._meta.app_label} | {IPAddress._meta.verbose_name}'

        return render(
            request,
            self.template_name,
            
            {
                # 'object_action': instance.action,
                'title': title,
                'diff_added': diff_added,
                'diff_removed': diff_removed,
                'incomming_change': incomming_change,
                'current_state': current_state,
                'updated_time': updated_time,
                'action': action,
                'object_type': object_type
            },
        )
    
class SlurpitPrefixEditView(generic.ObjectEditView):
    queryset = SlurpitPrefix.objects.all()
    model_form = SlurpitPrefixEditForm
    template_name = 'slurpit_nautobot/object_edit.html'

class SlurpitInterfaceEditView(generic.ObjectEditView):
    queryset = SlurpitInterface.objects.all()
    model_form = SlurpitInterfaceEditForm
    template_name = 'slurpit_nautobot/object_edit.html'

class SlurpitIPAddressEditView(generic.ObjectEditView):
    queryset = SlurpitIPAddress.objects.all()
    model_form = SlurpitIPAddressEditForm
    template_name = 'slurpit_nautobot/object_edit.html'

class SlurpitInterfaceBulkEditView(generic.BulkEditView):
    queryset = SlurpitInterface.objects.all()
    filterset = SlurpitInterfaceFilterSet
    table = tables.SlurpitInterfaceTable
    form = forms.SlurpitInterfaceBulkEditForm
    template_name = 'slurpit_nautobot/object_bulkedit.html'

class SlurpitPrefixBulkEditView(generic.BulkEditView):
    queryset = SlurpitPrefix.objects.all()
    filterset = SlurpitPrefixFilterSet
    table = tables.SlurpitPrefixTable
    form = forms.SlurpitPrefixBulkEditForm
    # template_name = 'slurpit_nautobot/object_bulkedit.html'

class SlurpitIPAddressBulkEditView(generic.BulkEditView):
    queryset = SlurpitIPAddress.objects.all()
    filterset = SlurpitIPAddressFilterSet
    table = tables.SlurpitIPAddressTable
    form = forms.SlurpitIPAddressBulkEditForm
    # template_name = 'slurpit_nautobot/object_bulkedit.html'
