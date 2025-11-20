import requests

from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import connection, transaction
from django.db.models import QuerySet, F, OuterRef, Subquery
from django.db.models import ManyToManyField, ManyToManyRel, F, Q, Func, Value
from django.utils.text import slugify
from django.utils import timezone
from django.db.models.expressions import RawSQL

from . import get_config
from .models import SlurpitImportedDevice, SlurpitStagedDevice, ensure_slurpit_tags, SlurpitSetting, SlurpitPlanning, SlurpitSnapshot, CharField
from .management.choices import *
from .references import base_name, plugin_type, custom_field_data_name
from .references.generic import get_default_objects, status_inventory, status_active, status_offline, get_create_dcim_objects, set_device_custom_fields, status_active_for_ipaddress, status_active_for_interface, status_active_for_prefix, status_active_for_location, status_retired_for_location
from .references.imports import *

from nautobot.dcim.models import Interface, Location
from nautobot.ipam.models import IPAddress
import netaddr

BATCH_SIZE = 256
columns = ('slurpit_id', 'disabled', 'hostname', 'fqdn', 'ipv4', 'device_os', 'device_type', 'brand', 'createddate', 'changeddate', 'location')


def get_devices(offset):
    try:
        setting = SlurpitSetting.objects.get()
        uri_base = setting.server_url
        headers = {
                        'authorization': setting.api_key,
                        'useragent': f"{plugin_type}/requests",
                        'accept': 'application/json'
                    }
        uri_devices = f"{uri_base}/api/devices?offset={offset}&limit={BATCH_SIZE}"
        r = requests.get(uri_devices, headers=headers, timeout=15, verify=False)
        # r.raise_for_status()
        data = r.json()
        log_message = f"Syncing the devices from Slurp'it in {plugin_type.capitalize()}."
        return data, ""
    except ObjectDoesNotExist:
        setting = None
        log_message = "Need to set the setting parameter"
        return None, log_message
    except Exception as e:
        log_message = "Please confirm the Slurp'it server is running and reachable."
        return None, log_message

def format_address(street, number, zipcode, country):
    return f"{street} {number} {zipcode} {country}"

def create_locations(data):
    for item in data:
        # First, format the address
        address = format_address(item['street'], item['number'], item['zipcode'], item['country'])

        if item['latitude'] == '':
            item['latitude'] = None
        
        if item['longitude'] == '':
            item['longitude'] = None

        if item['status'] == '1':
            status = status_active_for_location()
        else:
            status = status_retired_for_location()

        
        defaults= get_default_objects()
        default_location_type = defaults['location_type']

        description = ""
        if "description" in item:
            description = item['description']

        # Prepare data for the Location instance
        location_data = {
            'description': description,
            'longitude': item['longitude'],
            'latitude': item['latitude'],
            'status': status,
            'location_type': default_location_type,
            'physical_address': address,
            'shipping_address': address
        }
        # Update if exists, create if not
        location, created = Location.objects.update_or_create(
            name=item['sitename'],  # Field to match for finding the record
            defaults=location_data       # Fields to update or set if the object is created
        )

        if created:
            print(f"Created new location with name {item['sitename']}")
        else:
            print(f"Updated existing location with name {item['sitename']}")

def sync_locations():
    try:
        setting = SlurpitSetting.objects.get()
        uri_base = setting.server_url
        headers = {
                        'authorization': setting.api_key,
                        'useragent': f"{plugin_type}/requests",
                        'accept': 'application/json'
                    }
        uri_sites = f"{uri_base}/api/sites"
        r = requests.get(uri_sites, headers=headers, timeout=15, verify=False)
        data = r.json()

        # Import Slurpit Locations to NetBox
        create_locations(data)

        return data, ""
    except ObjectDoesNotExist:
        setting = None
        return None, ""
    except Exception as e:
        log_message = "Please confirm the Slurp'it server is running and reachable."
        return None, log_message
    
def start_device_import():
    with connection.cursor() as cursor:
        cursor.execute(f"truncate {SlurpitStagedDevice._meta.db_table} cascade")

def import_devices(devices):
    to_insert = []
    for device in devices:
        # if device.get('disabled') == '1':
        #     continue
        if device.get('device_type') is None:
            device['device_type'] = ''

        device['hostname'] = device['hostname'].lower()
        device['slurpit_id'] = device.pop('id')
        
        if 'site' in device:
            device['location'] = device.pop('site')
        if 'address' in device:
            device['ipv4'] = device.pop('address')
        try:
            device['createddate'] = timezone.make_aware(datetime.strptime(device['createddate'], '%Y-%m-%d %H:%M:%S'), timezone.get_current_timezone())
            device['changeddate'] = timezone.make_aware(datetime.strptime(device['changeddate'], '%Y-%m-%d %H:%M:%S'), timezone.get_current_timezone())          
        except ValueError:
            continue
        to_insert.append(SlurpitStagedDevice(**{key: value for key, value in device.items() if key in columns}))
    SlurpitStagedDevice.objects.bulk_create(to_insert)


def process_import(delete=True):
    if delete:
        handle_parted()
    handle_changed()
    handle_new_comers()
    

def run_import():
    devices = get_devices()
    if devices is not None:
        start_device_import()
        import_devices(devices)
        process_import()
        return 'done'
    else:
        return 'none'


def handle_parted():
    parted_qs = SlurpitImportedDevice.objects.exclude(
        slurpit_id__in=SlurpitStagedDevice.objects.values('slurpit_id')
    )
    
    count = 0
    for device in parted_qs:
        if device.mapped_device is None:
            device.delete()
        # elif device.mapped_device.status == status_offline():
        #     continue
        # else:
        #     device.mapped_device.status=status_offline()
        #     device.mapped_device.save()
        count += 1
    

def handle_new_comers():
    unattended = get_config('unattended_import')
    
    qs = SlurpitStagedDevice.objects.exclude(
        slurpit_id__in=SlurpitImportedDevice.objects.values('slurpit_id')
    )

    offset = 0
    count = len(qs)

    while offset < count:
        batch_qs = qs[offset:offset + BATCH_SIZE]
        to_import = []        
        for device in batch_qs:
            to_import.append(get_from_staged(device, unattended))
        SlurpitImportedDevice.objects.bulk_create(to_import, ignore_conflicts=True)
        offset += BATCH_SIZE


def handle_changed():
    latest_changeddate_subquery = SlurpitImportedDevice.objects.filter(
        slurpit_id=OuterRef('slurpit_id')
    ).order_by('-changeddate').values('changeddate')[:1]
    qs = SlurpitStagedDevice.objects.annotate(
        latest_changeddate=Subquery(latest_changeddate_subquery)
    ).filter(
        changeddate__gt=F('latest_changeddate')
    )
    offset = 0
    count = len(qs)

    while offset < count:
        batch_qs = qs[offset:offset + BATCH_SIZE]
        to_import = []        
        for device in batch_qs:
            result = SlurpitImportedDevice.objects.get(slurpit_id=device.slurpit_id)
            result.copy_staged_values(device)
            dtype = get_create_dcim_objects(device)
            result.mapped_devicetype = dtype

            result.save()
            
            if result.mapped_device:
                # if result.mapped_device.status==status_offline():
                #     result.mapped_device.status=status_active()
                if device.disabled == False:
                    if result.mapped_device.status==status_offline():
                        result.mapped_device.status=status_active()
                else:
                    if result.mapped_device.status != status_offline():
                        result.mapped_device.status=status_offline()

                    
                set_device_custom_fields(result.mapped_device, {
                    'slurpit_hostname': device.hostname,
                    'slurpit_fqdn': device.fqdn,
                    'slurpit_ipv4': device.ipv4,
                })   

                if device.ipv4:
                    #### Remove Primary IPv4 on other device
                    masked_hosts = bytes(netaddr.IPNetwork(f'{device.ipv4}/32').ip)
                    masked_prefixes = netaddr.IPNetwork(f'{device.ipv4}/32').prefixlen
                    other_device = Device.objects.filter(Q(primary_ip4__host=masked_hosts, primary_ip4__mask_length=masked_prefixes)).first()

                    if other_device:
                        other_device.primary_ip4 = None
                        other_device.save()

                    interface = Interface.objects.filter(device=result.mapped_device)
                    if interface:
                        interface = interface.first()
                    else:
                        interface = Interface.objects.create(name='management1', device=result.mapped_device, type='other')

                    address = f'{device.ipv4}/32'
                    ipaddress = IPAddress.objects.filter(address=address)
                    if ipaddress:
                        ipaddress = ipaddress.first()
                    else:
                        prefix = Prefix.objects.get_or_create(prefix=address, defaults={'status':status_active_for_prefix()})
                        ipaddress = IPAddress.objects.create(address=address, status=status_active_for_ipaddress())
                    
                    ipaddress.assigned_object = interface
                    ipaddress.save()
                    result.mapped_device.primary_ip4 = ipaddress

                result.mapped_device.name = device.hostname
                result.mapped_device.save()
        offset += BATCH_SIZE

def import_from_queryset(qs: QuerySet, **extra):
    count = len(qs)
    offset = 0

    while offset < count:
        batch_qs = qs[offset:offset + BATCH_SIZE]
        to_import = []        
        for device in batch_qs:
            device.mapped_device = get_dcim_device(device, **extra)
            to_import.append(device)
        SlurpitImportedDevice.objects.bulk_update(to_import, fields={'mapped_device_id'})
        offset += BATCH_SIZE

def get_dcim_device(staged: SlurpitStagedDevice | SlurpitImportedDevice, **extra) -> Device: 
    kw = get_default_objects()
    cf = extra.pop(custom_field_data_name, {})
    interface_name = extra.pop('interface_name', 'management1')
    del kw['location_type']
    cf.update({
        'slurpit_hostname': staged.hostname,
        'slurpit_fqdn': staged.fqdn,
        'slurpit_platform': staged.device_os,
        'slurpit_manufacturer': staged.brand,
        'slurpit_devicetype': staged.device_type,
        'slurpit_ipv4': staged.ipv4,
        'slurpit_location': staged.location
    })    

    platform = Platform.objects.get(name=staged.device_os)
    
    devicetype = None
    if 'device_type' in extra:
        devicetype = extra['device_type']
        staged.mapped_devicetype = extra['device_type']
        staged.save()

    elif 'device_type' not in extra and staged.mapped_devicetype is not None:
        devicetype = staged.mapped_devicetype
    
    # if devicetype:
    #     platform = devicetype.default_platform

        
    kw.update({
        'name': staged.hostname,
        'platform': platform,
        custom_field_data_name: cf,
        **extra,
        # 'primary_ip4_id': int(ip_address(staged.fqdn)),
    })
    if 'device_type' not in extra and staged.mapped_devicetype is not None:
        kw['device_type'] = staged.mapped_devicetype

    if staged.disabled == False:
        pass
        # kw.setdefault('status', status_active())
    else:
        kw.setdefault('status', status_offline())

    # device = Device.objects.filter(name=staged.hostname)

    # if device:
    #     device = device.first()
    #     device.update()
    # else:

    device = Device.objects.create(**kw)
    ensure_slurpit_tags(device)
    # Interface for new device.
    if staged.ipv4:
        #### Remove Primary IPv4 on other device
        masked_hosts = bytes(netaddr.IPNetwork(f'{staged.ipv4}/32').ip)
        masked_prefixes = netaddr.IPNetwork(f'{staged.ipv4}/32').prefixlen
        other_device = Device.objects.filter(Q(primary_ip4__host=masked_hosts, primary_ip4__mask_length=masked_prefixes)).first()

        if other_device:
            other_device.primary_ip4 = None
            other_device.save()

        interface, _ = Interface.objects.get_or_create(name=interface_name, device=device, defaults={'type': 'other', 'status': status_active_for_interface()})
        
        address = f'{staged.ipv4}/32'
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

    return device

def get_from_staged(
        staged: SlurpitStagedDevice,
        add_dcim: bool
) -> SlurpitImportedDevice:
    device = SlurpitImportedDevice()
    device.copy_staged_values(staged)

    device.mapped_devicetype = get_create_dcim_objects(staged)
    if add_dcim:
        extra = {'device_type': device.mapped_devicetype} if device.mapped_devicetype else {}
        device.mapped_device = get_dcim_device(staged, **extra)
    return device


    
def get_latest_data_on_planning(hostname, planning_id):
    try:
        setting = SlurpitSetting.objects.get()
        uri_base = setting.server_url
        headers = {
                        'authorization': setting.api_key,
                        'useragent': f"{plugin_type}/requests",
                        'accept': 'application/json'
                    }
        uri_devices = f"{uri_base}/api/devices/snapshot/single/{hostname}/{planning_id}"

        r = requests.get(uri_devices, headers=headers, timeout=15, verify=False)
        #r.raise_for_status()
        if r.status_code != 200:
            return None
        data = r.json()
        log_message = f"Get the latest data from Slurp'it in {plugin_type.capitalize()} on planning ID."
        return data
    except ObjectDoesNotExist:
        setting = None
        log_message = "Need to set the setting parameter"
        return None

def import_plannings(plannings, delete=True):
    ids = {str(row['id']) : row for row in plannings if row['disabled'] == '0'}

    with transaction.atomic():
        if delete:
            count = SlurpitPlanning.objects.exclude(planning_id__in=ids.keys()).delete()[0]
            SlurpitSnapshot.objects.filter(planning_id__in=ids.keys()).delete()
            
        update_objects = SlurpitPlanning.objects.filter(planning_id__in=ids.keys())
        for planning in update_objects:
            obj = ids.pop(str(planning.planning_id))
            planning.name = obj['name']
            planning.comments = obj['comment']
            planning.save()
        
        to_save = []
        for obj in ids.values():
            to_save.append(SlurpitPlanning(name=obj['name'], comments=obj['comment'], planning_id=obj['id']))
        SlurpitPlanning.objects.bulk_create(to_save)
        