import json

from rest_framework.routers import APIRootView
from rest_framework_bulk import BulkCreateModelMixin, BulkDestroyModelMixin
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status, mixins

from django.db import transaction
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from django.forms.models import model_to_dict

from nautobot.extras.api.views import NotesViewSetMixin

from .serializers import (
    SlurpitPlanningSerializer,
    SlurpitSnapshotSerializer,
    SlurpitImportedDeviceSerializer,
    SlurpitIPAddressSerializer,
    SlurpitInterfaceSerializer,
    SlurpitPrefixSerializer,
    SlurpitSettingSerializer
)
from ..validator import (
    device_validator, ipam_validator, interface_validator, prefix_validator
)
from ..importer import process_import, import_devices, import_plannings, start_device_import, BATCH_SIZE, create_locations, sync_locations
from ..management.choices import *
from ..views.datamapping import get_device_dict
from ..references import base_name 
from ..references.generic import status_offline, SlurpitViewSet, status_decommissioning
from ..references.imports import * 
from ..models import (
    SlurpitPlanning, 
    SlurpitSnapshot, 
    SlurpitImportedDevice, 
    SlurpitStagedDevice,
    SlurpitMapping, 
    SlurpitIPAddress, 
    SlurpitInterface, 
    SlurpitPrefix,
    SlurpitSetting
)
from ..filtersets import SlurpitPlanningFilterSet, SlurpitSnapshotFilterSet, SlurpitImportedDeviceFilterSet

# Import Models from Nautobot
from nautobot.ipam.models import (
    IPAddress, Namespace, get_default_namespace, VRF, Prefix, VRFPrefixAssignment
)
from nautobot.dcim.models import Interface, Location
from nautobot.extras.models import Status, Role
# Import Forms
from nautobot.ipam.forms import (
    IPAddressForm, PrefixForm
)
from nautobot.dcim.forms import InterfaceForm

from django.core.cache import cache

from nautobot.dcim.api.serializers import LocationSerializer

__all__ = (
    'SlurpitPlanningViewSet',
    'SlurpitRootView',
    'SlurpitDeviceView',
    'SlurpitSettingViewSet'
)

class SlurpitRootView(APIRootView):
    """
    Slurpit API root view
    """
    def get_view_name(self):
        return 'Slurpit'
    

class SlurpitPlanningViewSet(
        SlurpitViewSet
    ):
    queryset = SlurpitPlanning.objects.all()
    serializer_class = SlurpitPlanningSerializer
    filterset_class = SlurpitPlanningFilterSet

    
    def get_queryset(self):
        if self.request.method == 'GET':
            # Customize this queryset to suit your requirements for GET requests
            return SlurpitPlanning.objects.filter(selected=True)
        # For other methods, use the default queryset
        return self.queryset

class SlurpitSettingViewSet(SlurpitViewSet, NotesViewSetMixin):
    queryset = SlurpitSetting.objects.all()
    serializer_class = SlurpitSettingSerializer
class DeviceViewSet(
        SlurpitViewSet,
        BulkCreateModelMixin,
        BulkDestroyModelMixin,
    ):
    queryset = SlurpitImportedDevice.objects.all()
    serializer_class = SlurpitImportedDeviceSerializer
    filterset_class = SlurpitImportedDeviceFilterSet

    @action(detail=False, methods=['delete'], url_path='delete-all')
    def delete_all(self, request, *args, **kwargs):
        with transaction.atomic():
            Device.objects.select_related('slurpitimporteddevice').update(status=status_decommissioning())
            SlurpitStagedDevice.objects.all().delete()
            SlurpitImportedDevice.objects.filter(mapped_device__isnull=True).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['delete'], url_path='delete/(?P<hostname>[^/.]+)')
    def delete(self, request, *args, **kwargs):
        hostname_to_delete = kwargs.get('hostname')
        with transaction.atomic():
            to_delete = SlurpitImportedDevice.objects.filter(hostname=hostname_to_delete)
            if to_delete:
                Device.objects.filter(slurpit_imported_devices__in=to_delete).update(status=status_decommissioning())
                to_delete.delete()
                SlurpitStagedDevice.objects.filter(hostname=hostname_to_delete).delete()

        return JsonResponse({'status': 'ok'}, status=200)
    
    def create(self, request):
        # sync_locations()
        errors = device_validator(request.data)
        if errors:
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)
        if len(request.data) != 1:
            return JsonResponse({'status': 'error', 'errors': ['List size should be 1']}, status=400)
        
        start_device_import()
        import_devices(request.data)
        process_import(delete=False)
        
        return JsonResponse({'status': 'success'})
    
    @action(detail=False, methods=['post'],  url_path='sync')
    def sync(self, request):            
        errors = device_validator(request.data)
        if errors:
            return JsonResponse({'status': 'error', 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

        import_devices(request.data)        
        return JsonResponse({'status': 'success'})

    @action(detail=False, methods=['post'],  url_path='sync_start')
    def sync_start(self, request):
        # sync_locations()
        start_device_import()
        return JsonResponse({'status': 'success'})

    @action(detail=False, methods=['post'],  url_path='sync_end')
    def sync_end(self, request):
        process_import()
        return JsonResponse({'status': 'success'})
    
class SlurpitTestAPIView(SlurpitViewSet):
    queryset = SlurpitImportedDevice.objects.all()
    serializer_class = SlurpitImportedDeviceSerializer
    filterset_class = SlurpitImportedDeviceFilterSet

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='api')
    def api(self, request, *args, **kwargs):    
        return JsonResponse({'status': 'success'})
    
class SlurpitDeviceView(SlurpitViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    filterset_class = DeviceFilterSet


    @action(detail=False, methods=['get'], url_path='all')
    def all(self, request, *args, **kwargs):
        request_body = []

        devices_array = [get_device_dict(device) for device in Device.objects.all()]

        objs = SlurpitMapping.objects.all()
        
        for device in devices_array:
            row = {}
            for obj in objs:
                target_field = obj.target_field.split('|')[1]
                row[obj.source_field] = str(device[target_field])
            request_body.append(row)


        return JsonResponse({'data': request_body})


class SlurpitIPAMView(SlurpitViewSet):
    queryset = IPAddress.objects.all()

    def get_serializer_class(self):
        return SlurpitIPAddressSerializer

    def create(self, request):
        # Validate request IPAM data
        errors = ipam_validator(request.data)
        if errors:
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)

        namespace = None
        tenant = None
        role = None
        status = None

        try:
            # Get initial values for IPAM
            enable_reconcile = True
            initial_obj = SlurpitIPAddress.objects.filter(host=None)
            initial_ipaddress_values = {}
            ipaddress_update_ignore_values = []

            if initial_obj:
                initial_obj = initial_obj.values(
                    'status', 
                    'namespace', 
                    'type', 
                    'role', 
                    'tenant', 
                    'dns_name', 
                    'description', 
                    'enable_reconcile',
                    'ignore_status', 
                    'ignore_type', 
                    'ignore_role', 
                    'ignore_tenant', 
                    'ignore_description',
                    'ignore_dns_name'
                ).first()
                
                enable_reconcile = initial_obj['enable_reconcile']
                del initial_obj['enable_reconcile']
                initial_ipaddress_values = {**initial_obj}

                if initial_ipaddress_values['tenant'] is not None:
                    tenant = Tenant.objects.get(pk=initial_ipaddress_values['tenant'])
                if initial_ipaddress_values['namespace'] is not None:
                    namespace = Namespace.objects.get(pk=initial_ipaddress_values['namespace'])
                if initial_ipaddress_values['status'] is not None:
                    status = Status.objects.get(pk=initial_ipaddress_values['status'])
                if initial_ipaddress_values['role'] is not None:
                    role = Role.objects.get(pk=initial_ipaddress_values['role'])

                initial_ipaddress_values['tenant'] = tenant
                initial_ipaddress_values['namespace'] = namespace
                initial_ipaddress_values['status'] = status
                initial_ipaddress_values['role'] = role

                for key in initial_ipaddress_values.keys():
                    if key.startswith('ignore_') and initial_ipaddress_values[key]:
                        ipaddress_update_ignore_values.append(key)

            else:
                status = Status.objects.get(name='Active')
                namespace = get_default_namespace()
                initial_ipaddress_values['status'] = status
                initial_ipaddress_values['namespace'] = namespace 
                initial_ipaddress_values['type'] = 'dhcp'
                initial_ipaddress_values['tenant'] = None
                initial_ipaddress_values['role'] = None
                initial_ipaddress_values['description'] = ''
                initial_ipaddress_values['dns_name'] = ''

            total_errors = {}
            insert_ips = []
            update_ips = []
            total_ips = []

            duplicates = []
            # Form validation 
            for record in request.data[::-1]:
                unique_ipaddress = f'{record["address"]}'

                if unique_ipaddress in duplicates:
                    continue
                duplicates.append(unique_ipaddress)

                obj = IPAddress()
                new_data = {**initial_ipaddress_values, **record}

                new_data['status'] = Status.objects.get(name=new_data['status'])

                form = IPAddressForm(data=new_data, instance=obj)
                total_ips.append(new_data)
                
                # Fail case
                if form.is_valid() is False:
                    form_errors = form.errors
                    error_list_dict = {}

                    for field, errors in form_errors.items():
                        error_list_dict[field] = list(errors)

                    # Duplicate IP Address
                    keys = error_list_dict.keys()
                    if len(keys) ==1 and 'namespace' in keys and len(error_list_dict['namespace']) == 1 and error_list_dict['namespace'][0].startswith("No suitable"):
                        new_data['parent'] = None
                        insert_ips.append(new_data)
                        continue
                    if 'namespace' in keys and len(error_list_dict['namespace']) == 1 and error_list_dict['namespace'][0].startswith("No suitable"):
                        del error_list_dict['namespace']
                    
                    if len(keys) ==1 and '__all__' in keys and len(error_list_dict['__all__']) == 1 and error_list_dict['__all__'][0].endswith("already exists."):
                        update_ips.append(new_data)
                        continue
                    if '__all__' in keys and len(error_list_dict['__all__']) == 1 and error_list_dict['__all__'][0].endswith("already exists."):
                        del error_list_dict['__all__']
                    
                    error_key = f'{new_data["address"]}({"Global" if new_data["namespace"] is None else new_data["namespace"]})'
                    total_errors[error_key] = error_list_dict

                    return JsonResponse({'status': 'error', 'errors': total_errors}, status=400)
                else:
                    ipaddress_obj = IPAddress.objects.filter(address=new_data['address'], parent__namespace=namespace)

                    if ipaddress_obj:
                        ipaddress_obj = ipaddress_obj.first()
                        new_data['parent'] = ipaddress_obj.parent
                        update_ips.append(new_data)
                    else:
                        insert_ips.append(new_data)

            if enable_reconcile:
                batch_update_qs = []
                batch_insert_qs = []

                for item in total_ips:

                    slurpit_ipaddress_item = SlurpitIPAddress.objects.filter(address=item['address'], namespace=item['namespace'])
                    # slurpit_ipaddress_item = SlurpitIPAddress.objects.filter(address=item['address'])

                    if slurpit_ipaddress_item:
                        slurpit_ipaddress_item = slurpit_ipaddress_item.first()

                        allowed_fields_with_none = {'status'}
                        allowed_fields = {'role', 'tenant', 'type', 'dns_name', 'description'}

                        for field, value in item.items():
                            if field in allowed_fields and value is not None and value != "":
                                setattr(slurpit_ipaddress_item, field, value)
                            if field in allowed_fields_with_none:
                                setattr(slurpit_ipaddress_item, field, value)

                        batch_update_qs.append(slurpit_ipaddress_item)
                    else:
                        obj = IPAddress.objects.filter(address=item['address'], parent__namespace=namespace)
                        
                        fields = ['status', 'role', 'tenant', 'type', 'dns_name', 'description']
                        not_null_fields = {'role', 'tenant', 'type', 'dns_name', 'description'}

                        new_ipaddress = {}

                        if obj:
                            obj = obj.first()
                            old_ipaddress = {}
                            
                            for field in fields:
                                field_name = f'ignore_{field}'
                                if field_name in ipaddress_update_ignore_values:
                                    continue
                                old_ipaddress[field] = getattr(obj, field)
                                new_ipaddress[field] = item[field]

                                if field in not_null_fields and (new_ipaddress[field] is None or new_ipaddress[field] == ""):
                                    new_ipaddress[field] = old_ipaddress[field]

                            if new_ipaddress == old_ipaddress:
                                continue
                        else:
                            for field in fields:
                                new_ipaddress[field] = item[field]

                        obj = SlurpitIPAddress(
                            address = item['address'], 
                            namespace = namespace,
                            **new_ipaddress
                        )

                        batch_insert_qs.append(obj)
                
                count = len(batch_insert_qs)
                offset = 0

                while offset < count:
                    batch_qs = batch_insert_qs[offset:offset + BATCH_SIZE]
                    to_import = []        
                    for ipaddress_item in batch_qs:
                        to_import.append(ipaddress_item)
                    created_items = SlurpitIPAddress.objects.bulk_create(to_import)
                    offset += BATCH_SIZE



                count = len(batch_update_qs)
                offset = 0
                while offset < count:
                    batch_qs = batch_update_qs[offset:offset + BATCH_SIZE]
                    to_import = []        
                    for ipaddress_item in batch_qs:
                        to_import.append(ipaddress_item)
                    SlurpitIPAddress.objects.bulk_update(to_import, fields={'status', 'type', 'role', 'tenant', 'dns_name', 'description'})
                    offset += BATCH_SIZE
                
            else:
                
                # Batch Insert
                count = len(insert_ips)
                offset = 0
                while offset < count:
                    batch_qs = insert_ips[offset:offset + BATCH_SIZE]
                    to_import = []        
                    for ipaddress_item in batch_qs:
                        filtered_ipaddress_item = {k: v for k, v in ipaddress_item.items() if not k.startswith('ignore_')}
                        item = IPAddress(**filtered_ipaddress_item)

                        parent = None
                        try:
                            parent = item._get_closest_parent()
                        except:
                            parent = None

                        if parent is None:
                            status = Status.objects.get(name='Active')
                            parent = Prefix.objects.create(prefix=f'{item.host}/32', namespace=namespace, status = status)

                        filtered_ipaddress_item['parent'] = parent
                        to_import.append(IPAddress(**filtered_ipaddress_item))
                    IPAddress.objects.bulk_create(to_import)

                    offset += BATCH_SIZE
                
                # Batch Update
                batch_update_qs = []
                for update_item in update_ips:
                    item = IPAddress.objects.get(address=update_item['address'], parent=update_item['parent'])

                    # Update
                    allowed_fields_with_none = {'status'}
                    allowed_fields = {'role', 'tenant', 'type', 'dns_name', 'description'}

                    for field, value in update_item.items():
                        ignore_field = f'ignore_{field}'
                        if ignore_field in ipaddress_update_ignore_values:
                            continue 

                        if field in allowed_fields and value is not None and value != "":
                            setattr(item, field, value)
                        if field in allowed_fields_with_none:
                            setattr(item, field, value)

                    batch_update_qs.append(item)

                count = len(batch_update_qs)
                offset = 0
                while offset < count:
                    batch_qs = batch_update_qs[offset:offset + BATCH_SIZE]
                    to_import = []        
                    for ipaddress_item in batch_qs:
                        to_import.append(ipaddress_item)

                    IPAddress.objects.bulk_update(to_import, fields={'status', 'role', 'tenant', 'dns_name', 'description', 'type'})
                    offset += BATCH_SIZE

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'errors': str(e)}, status=400)

class SlurpitInterfaceView(SlurpitViewSet):
    queryset = Interface.objects.all()

    def get_serializer_class(self):
        return SlurpitInterfaceSerializer
    
    def create(self, request):
        # Validate request Interface data
        errors = interface_validator(request.data)
        if errors:
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)

        vrf = None
        status = None

        try:
            # Get initial values for Interface
            enable_reconcile = True
            initial_obj = SlurpitInterface.objects.filter(name='')
            initial_interface_values = {}
            interface_update_ignore_values = []

            if initial_obj:
                initial_obj = initial_obj.values(
                    'status', 
                    'label', 
                    'type', 
                    'vrf', 
                    'mode', 
                    'description', 
                    'enable_reconcile',
                    'ignore_status',
                    'ignore_label',
                    'ignore_type',
                    'ignore_vrf',
                    'ignore_description',
                    'ignore_mode'
                ).first()
                
                enable_reconcile = initial_obj['enable_reconcile']
                del initial_obj['enable_reconcile']
                initial_interface_values = {**initial_obj}

                if initial_interface_values['status'] is not None:
                    status = Status.objects.get(pk=initial_interface_values['status'])
                if initial_interface_values['vrf'] is not None:
                    vrf = VRF.objects.get(pk=initial_interface_values['vrf'])

                initial_interface_values['status'] = status
                initial_interface_values['vrf'] = vrf

                for key in initial_interface_values.keys():
                    if key.startswith('ignore_') and initial_interface_values[key]:
                        interface_update_ignore_values.append(key)


            else:
                status = Status.objects.get(name='Active')
                initial_interface_values['status'] = status
                initial_interface_values['label'] = ''
                initial_interface_values['type'] = 'other'
                initial_interface_values['vrf'] = None
                initial_interface_values['mode'] = 'access'
                initial_interface_values['description'] = ''
                

            total_errors = {}
            insert_data = []
            update_data = []
            total_data = []
            duplicates = []

            # Form validation 
            for record in request.data[::-1]:
                unique_interface = f'{record["name"]}/{record["hostname"]}'
                if unique_interface in duplicates:
                    continue
                duplicates.append(unique_interface)

                device = None
                try:
                    device = Device.objects.get(name=record['hostname'])
                except: 
                    device = None

                if device is None: 
                    continue

                obj = Interface(device=device)
                record['device'] = device
                del record['hostname']

                if 'status' in record:
                    if record['status'] == 'up':
                        record['enabled'] = True
                    else:
                        record['enabled'] = False
                    del record['status']
                
                if 'description' in record:
                    record['description'] = str(record['description'])
                    
                new_data = {**initial_interface_values, **record}

                form = InterfaceForm(data=new_data, instance=obj)
                total_data.append(new_data)
                
                # Fail case
                if form.is_valid() is False:
                    form_errors = form.errors
                    error_list_dict = {}
                    for field, errors in form_errors.items():
                        error_list_dict[field] = list(errors)

                    # Duplicate IP Address
                    keys = error_list_dict.keys()
                    
                    if len(keys) ==1 and '__all__' in keys and len(error_list_dict['__all__']) == 1 and error_list_dict['__all__'][0].endswith("already exists."):
                        update_data.append(new_data)
                        continue
                    if '__all__' in keys and len(error_list_dict['__all__']) == 1 and error_list_dict['__all__'][0].endswith("already exists."):
                        del error_list_dict['__all__']

                    error_key = f'{new_data["name"]}({"Global" if new_data["device"] is None else new_data["device"]})'
                    total_errors[error_key] = error_list_dict

                    return JsonResponse({'status': 'error', 'errors': total_errors}, status=400)
                else:
                    insert_data.append(new_data)

            if enable_reconcile:
                batch_update_qs = []
                batch_insert_qs = []

                for item in total_data:
                    device = None
                    if item['device'] is not None:
                        device = Device.objects.get(name=item['device'])
                        
                    item['device'] = device
                    
                    slurpit_interface_item = SlurpitInterface.objects.filter(name=item['name'], device=item['device'])
                    
                    if slurpit_interface_item:
                        slurpit_interface_item = slurpit_interface_item.first()

                            # Update
                        allowed_fields_with_none = {'status'}
                        allowed_fields = {'label', 'type', 'vrf', 'mode', 'description', 'enabled'}

                        for field, value in item.items():
                            if field in allowed_fields and value is not None and value != "":
                                setattr(slurpit_interface_item, field, value)
                            if field in allowed_fields_with_none:
                                setattr(slurpit_interface_item, field, value)

                        batch_update_qs.append(slurpit_interface_item)
                    else:
                        obj = Interface.objects.filter(name=item['name'], device=item['device'])

                        fields = {'label', 'status', 'type', 'vrf', 'mode', 'description', 'enabled'}
                        not_null_fields = {'label', 'type', 'vrf', 'mode', 'description', 'enabled'}

                        new_interface = {}
                        if obj:
                            obj = obj.first()
                            old_interface = {}

                            for field in fields:
                                field_name = f'ignore_{field}'
                                if field_name in interface_update_ignore_values:
                                    continue
                                old_interface[field] = getattr(obj, field)
                                new_interface[field] = item[field]

                                if field in not_null_fields and (new_interface[field] is None or new_interface[field] == ""):
                                    new_interface[field] = old_interface[field]

                            if new_interface == old_interface:
                                continue
                        else:
                            for field in fields: 
                                new_interface[field] = item[field]

                        batch_insert_qs.append(SlurpitInterface(
                            name = item['name'], 
                            device = device,
                            **new_interface
                        ))
                
                count = len(batch_insert_qs)
                offset = 0

                while offset < count:
                    batch_qs = batch_insert_qs[offset:offset + BATCH_SIZE]
                    to_import = []        
                    for interface_item in batch_qs:
                        to_import.append(interface_item)

                    SlurpitInterface.objects.bulk_create(to_import)
                    offset += BATCH_SIZE


                count = len(batch_update_qs)
                offset = 0
                while offset < count:
                    batch_qs = batch_update_qs[offset:offset + BATCH_SIZE]
                    to_import = []        
                    for interface_item in batch_qs:
                        to_import.append(interface_item)

                    SlurpitInterface.objects.bulk_update(to_import, 
                        fields={'label', 'status', 'type', 'mode', 'description', 'vrf'}
                    )
                    offset += BATCH_SIZE
                
            else:
                # Batch Insert
                count = len(insert_data)
                offset = 0
                while offset < count:
                    batch_qs = insert_data[offset:offset + BATCH_SIZE]
                    to_import = []        
                    for interface_item in batch_qs:
                        filtered_interface_item = {k: v for k, v in interface_item.items() if not k.startswith('ignore_')}
                        to_import.append(Interface(**filtered_interface_item))
                    Interface.objects.bulk_create(to_import)
                    offset += BATCH_SIZE
                
                
                # Batch Update
                batch_update_qs = []
                for update_item in update_data:
                    item = Interface.objects.get(name=update_item['name'], device=update_item['device'])
                    
                    # Update
                    allowed_fields_with_none = {'status'}
                    allowed_fields = {'label', 'type', 'vrf', 'mode', 'description'}

                    for field, value in update_item.items():
                        ignore_field = f'ignore_{field}'
                        if ignore_field in interface_update_ignore_values:
                            continue 

                        if field in allowed_fields and value is not None and value != "":
                            setattr(item, field, value)
                        if field in allowed_fields_with_none:
                            setattr(item, field, value)

                    batch_update_qs.append(item)

                
                count = len(batch_update_qs)
                offset = 0
                while offset < count:
                    batch_qs = batch_update_qs[offset:offset + BATCH_SIZE]
                    to_import = []        
                    for interface_item in batch_qs:
                        to_import.append(interface_item)

                    Interface.objects.bulk_update(to_import, 
                        fields={'label', 'status', 'type', 'mode', 'description', 'vrf'}
                    )
                    offset += BATCH_SIZE

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'errors': str(e)}, status=400)

class SlurpitPrefixView(SlurpitViewSet):
    queryset = Prefix.objects.all()

    @action(detail=False, methods=['get'], url_path='all')
    def all(self, request, *args, **kwargs):
        prefixes = Prefix.objects.filter(tags__name="slurpit")
        prefixes_data = list(prefixes.values())

        prefixes = []
        for prefix in prefixes_data:
            prefixes.append(f'{prefix["network"]}/{prefix["prefix_length"]}')
        return JsonResponse(prefixes, safe=False)
    
    def get_serializer_class(self):
        return SlurpitIPAddressSerializer
    
    def create(self, request):
        # Validate request Prefix data
        errors = prefix_validator(request.data)
        if errors:
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)

        namespace = None
        role = None
        tenant = None
        status = None

        try:
            # Get initial values for Prefix
            enable_reconcile = True
            initial_obj = SlurpitPrefix.objects.filter(network=None)
            initial_prefix_values = {}
            prefix_update_ignore_values = []

            if initial_obj:
                initial_obj = initial_obj.values(
                    'status', 
                    'namespace', 
                    'type', 
                    'role', 
                    'tenant', 
                    'description', 
                    'enable_reconcile',
                    'ignore_status',
                    'ignore_type',
                    'ignore_role',
                    'ignore_tenant',
                    'ignore_description'
                ).first()
                
                enable_reconcile = initial_obj['enable_reconcile']
                del initial_obj['enable_reconcile']
                initial_prefix_values = {**initial_obj}

                if initial_prefix_values['status'] is not None:
                    status = Status.objects.get(pk=initial_prefix_values['status'])
                if initial_prefix_values['tenant'] is not None:
                    tenant = Tenant.objects.get(pk=initial_prefix_values['tenant'])
                if initial_prefix_values['namespace'] is not None:
                    namespace = Namespace.objects.get(pk=initial_prefix_values['namespace'])
                if initial_prefix_values['role'] is not None:
                    role = Role.objects.get(pk=initial_prefix_values['role'])
                    
                initial_prefix_values['status'] = status
                initial_prefix_values['tenant'] = tenant
                initial_prefix_values['namespace'] = namespace
                initial_prefix_values['role'] = role

                for key in initial_prefix_values.keys():
                    if key.startswith('ignore_') and initial_prefix_values[key]:
                        prefix_update_ignore_values.append(key)

            else:
                status = Status.objects.get(name='Active')
                initial_prefix_values['status'] = status
                initial_prefix_values['namespace'] = get_default_namespace()
                initial_prefix_values['type'] = 'network'
                initial_prefix_values['role'] = None
                initial_prefix_values['tenant'] = None
                initial_prefix_values['description'] = ''
                

            total_errors = {}
            insert_data = []
            update_data = []
            total_data = []

            duplicates = []
            # Form validation 
            for record in request.data[::-1]:
                unique_prefix = f'{record["prefix"]}'

                if unique_prefix in duplicates:
                    continue
                duplicates.append(unique_prefix)

                obj = Prefix()
                
                new_data = {**initial_prefix_values, **record}
                new_data_without_vrf = {**new_data}

                del new_data_without_vrf['vrf']

                form = PrefixForm(data=new_data_without_vrf, instance=obj)

                total_data.append(new_data)

                # Fail case
                if form.is_valid() is False:
                    form_errors = form.errors
                    error_list_dict = {}

                    for field, errors in form_errors.items():
                        error_list_dict[field] = list(errors)

                    # Duplicate Prefix
                    keys = error_list_dict.keys()
                    
                    if len(keys) ==1 and '__all__' in keys and len(error_list_dict['__all__']) == 1 and error_list_dict['__all__'][0].endswith("already exists."):
                        update_data.append(new_data)
                        continue
                    if '__all__' in keys and len(error_list_dict['__all__']) == 1 and error_list_dict['__all__'][0].endswith("already exists."):
                        del error_list_dict['__all__']
                    
                    error_key = f'{new_data["prefix"]}({"Global" if new_data["namespace"] is None else new_data["namespace"]})'
                    total_errors[error_key] = error_list_dict

                    return JsonResponse({'status': 'error', 'errors': total_errors}, status=400)
                else:
                    insert_data.append(new_data)
            
            if enable_reconcile:
                batch_update_qs = []
                batch_insert_qs = []

                for item in total_data:                    
                    slurpit_prefix_item = SlurpitPrefix.objects.filter(prefix=item['prefix'], namespace=item['namespace'])
                    
                    if slurpit_prefix_item:
                        slurpit_prefix_item = slurpit_prefix_item.first()
                        
                        allowed_fields_with_none = {'status', 'vrf'}
                        allowed_fields = {'type', 'role', 'tenant', 'description'}

                        for field, value in item.items():
                            if field in allowed_fields and value is not None and value != "":
                                setattr(slurpit_prefix_item, field, value)
                            if field in allowed_fields_with_none:
                                setattr(slurpit_prefix_item, field, value)

                        batch_update_qs.append(slurpit_prefix_item)
                    else:
                        temp = Prefix(prefix=item['prefix'], namespace=item['namespace'], status=item['status'])
                        obj = Prefix.objects.filter(network=temp.network, prefix_length=temp.prefix_length, namespace=item['namespace'])

                        fields = {'status', 'type', 'role', 'tenant', 'description', 'vrf'}
                        not_null_fields = {'type', 'role', 'tenant', 'description'}
                        new_prefix = {}

                        if obj:
                            obj = obj.first()
                            old_prefix = {}
                            
                            for field in fields:
                                field_name = f'ignore_{field}'
                                if field_name in prefix_update_ignore_values:
                                    continue

                                if field == "vrf":
                                    # Assuming that VRFPrefixAssignment has a ForeignKey or similar to VRF model
                                    vrf_names = VRFPrefixAssignment.objects.filter(prefix=obj).values_list('vrf__name', flat=True)
                                    joined_vrf_names = ', '.join(vrf_names)
                                    old_prefix[field] = joined_vrf_names
                                    
                                else:
                                    old_prefix[field] = getattr(obj, field)

                                new_prefix[field] = item[field]

                                if field in not_null_fields and (new_prefix[field] is None or new_prefix[field] == ""):
                                    new_prefix[field] = old_prefix[field]

                            if new_prefix == old_prefix:
                                continue
                        else:
                            for field in fields:
                                new_prefix[field] = item[field]
                        
                        batch_insert_qs.append(SlurpitPrefix(
                            prefix = item['prefix'], 
                            namespace = item['namespace'],
                            **new_prefix
                        ))
                
                count = len(batch_insert_qs)
                offset = 0

                while offset < count:
                    batch_qs = batch_insert_qs[offset:offset + BATCH_SIZE]
                    to_import = []        
                    for prefix_item in batch_qs:
                        to_import.append(prefix_item)

                    SlurpitPrefix.objects.bulk_create(to_import)
                    offset += BATCH_SIZE

                count = len(batch_update_qs)
                offset = 0
                while offset < count:
                    batch_qs = batch_update_qs[offset:offset + BATCH_SIZE]
                    to_import = []        
                    for prefix_item in batch_qs:
                        to_import.append(prefix_item)

                    SlurpitPrefix.objects.bulk_update(to_import, 
                        fields={'status', 'role', 'type', 'vrf', 'tenant', 'description'}
                    )
                    offset += BATCH_SIZE
                
            else:
                # Batch Insert
                count = len(insert_data)
                offset = 0
                while offset < count:
                    batch_qs = insert_data[offset:offset + BATCH_SIZE]
                    to_import = []       

                    for prefix_item in batch_qs:
                        filtered_prefix_item = {k: v for k, v in prefix_item.items() if not k.startswith('ignore_')}
                        
                        new_prefix_item = {**filtered_prefix_item}
                        del new_prefix_item['vrf']

                        to_import.append(Prefix(**new_prefix_item))
                    
                    Prefix.objects.bulk_create(to_import)

                    for prefix_item in batch_qs:
                        temp = Prefix(
                            prefix=prefix_item['prefix'], 
                            namespace=prefix_item['namespace'], 
                            status=prefix_item['status'])
                    
                        nautobot_prefix = Prefix.objects.filter(
                            network=temp.network, 
                            prefix_length=temp.prefix_length, 
                            namespace=prefix_item['namespace']).first()
 
                        # Update VRF
                        if nautobot_prefix:
                            VRFPrefixAssignment.objects.filter(
                                prefix=nautobot_prefix
                            ).delete()

                            if prefix_item['vrf'] != "":
                            
                                new_vrf = VRF.objects.filter(
                                    name = prefix_item['vrf'],
                                    namespace=prefix_item['namespace']
                                ).first()

                                if new_vrf is None:
                                    new_vrf = VRF.objects.create(
                                        name = prefix_item['vrf'],
                                        namespace=prefix_item['namespace']
                                    )
                            
                                new_vrf.prefixes.add(nautobot_prefix)
                        
                    offset += BATCH_SIZE
                
                
                # Batch Update
                batch_update_qs = []
                for update_item in update_data:
                    filtered_update_item = {k: v for k, v in update_item.items() if not k.startswith('ignore_')}
                    
                    update_vrf = filtered_update_item['vrf']
                    del filtered_update_item['vrf']
                    temp = Prefix(**filtered_update_item)

                    item = Prefix.objects.get(network=temp.network, prefix_length=temp.prefix_length, namespace=update_item['namespace'])
                    
                    # Update
                    allowed_fields_with_none = {'status'}
                    allowed_fields = {'type', 'role', 'tenant', 'description'}

                    for field, value in update_item.items():
                        ignore_field = f'ignore_{field}'
                        if ignore_field in prefix_update_ignore_values:
                            continue 

                        if field in allowed_fields and value is not None and value != "":
                            setattr(item, field, value)
                        if field in allowed_fields_with_none:
                            setattr(item, field, value)

                    batch_update_qs.append(item)

                    # new_vrf.prefixes.clear()
                    VRFPrefixAssignment.objects.filter(
                        prefix=item
                    ).delete()

                    if update_vrf != "":
                        # Update VRF
                        new_vrf = VRF.objects.filter(
                            name = update_vrf,
                            namespace=item.namespace
                        ).first()

                        if new_vrf is None:
                            new_vrf = VRF.objects.create(
                                name = update_vrf,
                                namespace=item.namespace
                            )

                        new_vrf.prefixes.add(item)

                count = len(batch_update_qs)
                offset = 0
                while offset < count:
                    batch_qs = batch_update_qs[offset:offset + BATCH_SIZE]
                    to_import = []        
                    for prefix_item in batch_qs:
                        to_import.append(prefix_item)

                    Prefix.objects.bulk_update(to_import, 
                        fields={'role', 'status', 'type', 'tenant', 'description'}
                    )
                    offset += BATCH_SIZE

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'errors': str(e)}, status=400)
class SlurpitLocationView(SlurpitViewSet):
    queryset = Location.objects.all()
    
    def get_serializer_class(self):
        return LocationSerializer
    
    def create(self, request):
        try:
            create_locations(request.data[::-1])
        except Exception as e:
            return JsonResponse({'status': 'errors', 'errors': str(e)}, status=400)

        return JsonResponse({'status': 'success'})