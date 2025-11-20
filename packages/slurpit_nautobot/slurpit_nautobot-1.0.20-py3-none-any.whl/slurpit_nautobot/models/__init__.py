from nautobot.dcim.models import DeviceType, Manufacturer, Device
from django.contrib.contenttypes.models import ContentType
from nautobot.extras.choices import CustomFieldTypeChoices
from nautobot.extras.models import CustomField
from nautobot.extras.models.tags import Tag
from nautobot.tenancy.models import Tenant
from nautobot.dcim.models import Location, LocationType
from nautobot.extras.models import Status,Role

from django.db.models import Q, Transform, CharField, TextField

from .. import get_config
from .device import SlurpitImportedDevice, SlurpitStagedDevice
from .planning import SlurpitPlanning, SlurpitSnapshot
from .setting import SlurpitSetting
from .mapping import SlurpitMapping
from .ipam import SlurpitIPAddress
from .interface import SlurpitInterface
from .prefix import SlurpitPrefix

__all__ = [
    'SlurpitImportedDevice', 'SlurpitStagedDevice',
    'post_migration', 'SlurpitSetting'
]

def ensure_slurpit_tags(*items):
    if (tags := getattr(ensure_slurpit_tags, 'cache', None)) is None:
        name = 'slurpit'
        tag, _ = Tag.objects.get_or_create(name=name, defaults={'description':'Slurp\'it onboarded', 'color': 'F09640'})

        dcim_applicable_to = 'device', 'devicetype', 'manufacturer'
        ipam_applicable_to = 'iprange', 'prefix'

        dcim_Q = Q(app_label='dcim', model__in=dcim_applicable_to)
        ipam_Q = Q(app_label='ipam', model__in=ipam_applicable_to)
        tagged_types = ContentType.objects.filter(ipam_Q | dcim_Q)
        tag.content_types.set(tagged_types.all())
        tags = {tag}
        ensure_slurpit_tags.cache = tags
    for item in items:
        item.tags.set(tags)
    return tags

def create_custom_fields():   
    device = ContentType.objects.get(app_label='dcim', model='device')
    cf, _ = CustomField.objects.get_or_create(
                key='slurpit_hostname',  
                defaults = {
                    'type' : CustomFieldTypeChoices.TYPE_TEXT,
                    'description' : "",
                    'label' : 'Hostname',
                    'grouping' : "Slurp'it",
                }             
        )
    cf.content_types.set({device})

    cf, _ = CustomField.objects.get_or_create(
                key='slurpit_fqdn',     
                defaults = { 
                    'type' : CustomFieldTypeChoices.TYPE_TEXT,
                    'description' : "",
                    'label' : 'Fqdn',
                    'grouping' : "Slurp'it",
                }
            )
    cf.content_types.set({device})
        
    cf, _ = CustomField.objects.get_or_create(
                key='slurpit_platform',
                defaults = {
                    'type' : CustomFieldTypeChoices.TYPE_TEXT,
                    'description' : "",
                    'label' : 'Platform',
                    'grouping' : "Slurp'it",
                }
                
            )
    cf.content_types.set({device})

    cf, _ = CustomField.objects.get_or_create(
                key='slurpit_manufacturer', 
                defaults = {
                    'type' : CustomFieldTypeChoices.TYPE_TEXT,
                    'description' : "",
                    'label' : 'Manufacturer',
                    'grouping' : "Slurp'it",
                }
            )
    cf.content_types.set({device})
    
    cf, _ = CustomField.objects.get_or_create(
                key='slurpit_devicetype',
                defaults = {
                    'type' : CustomFieldTypeChoices.TYPE_TEXT,
                    'description' : "",
                    'label' : 'Device Type',
                    'grouping' : "Slurp'it",
                }
            )
    cf.content_types.set({device})
    
    cf, _ = CustomField.objects.get_or_create(
                key='slurpit_ipv4',
                defaults = {
                    'type' : CustomFieldTypeChoices.TYPE_TEXT,
                    'description' : "",
                    'label' : 'Ipv4',
                    'grouping' : "Slurp'it",
                }
            )
    cf.content_types.set({device})

    cf, _ = CustomField.objects.get_or_create(
                key='slurpit_location',
                defaults = {
                    'type' : CustomFieldTypeChoices.TYPE_TEXT,
                    'description' : "",
                    'label' : 'Location',
                    'grouping' : "Slurp'it",
                }    
            )
    cf.content_types.set({device})

def create_default_data_mapping():
    SlurpitMapping.objects.all().delete()

    mappings = [
        {"source_field": "hostname", "target_field": "device|name", "mapping_type": "device"},
        {"source_field": "fqdn", "target_field": "device|primary_ip4", "mapping_type": "device"},
        {"source_field": "ipv4", "target_field": "device|primary_ip4", "mapping_type": "device"},
        {"source_field": "device_os", "target_field": "device|platform", "mapping_type": "device"},
        {"source_field": "device_type", "target_field": "device|device_type", "mapping_type": "device"},
    ]
    for mapping in mappings:
        SlurpitMapping.objects.get_or_create(**mapping)


def add_default_mandatory_objects():
    manu, _ = Manufacturer.objects.get_or_create(**get_config('Manufacturer'))
    dtype, _ = DeviceType.objects.get_or_create(manufacturer=manu, **get_config('DeviceType'))
    tenant, _ = Tenant.objects.get_or_create(**get_config('Tenant'))
    location_type, _ = LocationType.objects.get_or_create(**get_config('LocationType'))
    location_type.content_types.add(ContentType.objects.get_for_model(Device))
    location_active_status = Status.objects.get_for_model(Location).all()[0]
    location, _ = Location.objects.get_or_create(location_type=location_type, status=location_active_status, **get_config('Location'))
    role, _ = Role.objects.get_or_create(**get_config('Role'))
    device = ContentType.objects.get(app_label='dcim', model='device')
    role.content_types.set({device})

    create_default_data_mapping()


def post_migration(sender, **kwargs):
    create_custom_fields()
    tags = ensure_slurpit_tags()
    add_default_mandatory_objects()
    pass