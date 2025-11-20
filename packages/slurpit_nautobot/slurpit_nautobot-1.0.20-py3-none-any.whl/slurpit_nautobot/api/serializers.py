from nautobot.core.api import NautobotModelSerializer, RelationshipModelSerializerMixin, CustomFieldModelSerializerMixin, ValidatedModelSerializer
from rest_framework import serializers
from nautobot.ipam.api.fields import IPFieldSerializer

from slurpit_nautobot.models import SlurpitPlanning, SlurpitImportedDevice, SlurpitStagedDevice, SlurpitSetting, SlurpitSnapshot, SlurpitMapping, SlurpitInterface, SlurpitPrefix, SlurpitIPAddress

__all__ = (
    'SlurpitPlanningSerializer',
    'SlurpitStagedDeviceSerializer',
    'SlurpitImportedDeviceSerializer',
    'SlurpitSettingSerializer',
    'SlurpitSnapshotSerializer',
    'SlurpitInterfaceSerializer',
    'SlurpitPrefixSerializer',
    'SlurpitIPAddressSerializer'
)

class SlurpitPlanningSerializer(NautobotModelSerializer):
    id = serializers.IntegerField(source='planning_id')
    comment = serializers.CharField(source='comments')

    class Meta:
        model = SlurpitPlanning
        fields = ['id', "name", "comment", "display"]

class SlurpitStagedDeviceSerializer(NautobotModelSerializer):
    id = serializers.IntegerField(source='slurpit_id')
    class Meta:
        model = SlurpitStagedDevice
        fields = ['id', 'disabled', 'hostname', 'fqdn', 'ipv4', 'device_os', 'device_type', 'brand', 'createddate', 'changeddate']

class SlurpitSnapshotSerializer(NautobotModelSerializer):
    class Meta:
        model = SlurpitSnapshot
        fields = ['id', 'hostname', 'planning_id', 'content', 'result_type']


class SlurpitImportedDeviceSerializer(NautobotModelSerializer):
    id = serializers.IntegerField(source='slurpit_id')
    class Meta:
        model = SlurpitImportedDevice
        fields = ['id', 'disabled', 'hostname', 'fqdn', 'ipv4', 'device_os', 'device_type', 'brand', 'createddate', 'changeddate']
        
class SlurpitSettingSerializer(NautobotModelSerializer):
    class Meta:
        model = SlurpitSetting
        fields = ['server_url', 'api_key', 'last_synced', 'connection_status', 'push_api_key', 'appliance_type']

class SlurpitMappingSerializer(NautobotModelSerializer):
    class Meta:
        model = SlurpitMapping
        fields = ['source_field', 'target_field', 'mapping_type']


class SlurpitInterfaceSerializer(
    RelationshipModelSerializerMixin, CustomFieldModelSerializerMixin, ValidatedModelSerializer
):
    class Meta:
        model = SlurpitInterface
        fields = [
            'id', 'name', 'status', 'device', 'label', 'type', 'description', 'mode', 'enabled', 'vrf',
            'custom_fields', 'created', 'last_updated'
        ]

class SlurpitPrefixSerializer(
    RelationshipModelSerializerMixin, CustomFieldModelSerializerMixin, ValidatedModelSerializer
):
    prefix = IPFieldSerializer()
    class Meta:
        model = SlurpitPrefix
        fields = [
             'id', 'prefix', 'status', 'namespace', 'type', 'role', 'date_allocated', 'tenant', 'description',
             'custom_fields', 'created', 'last_updated',
        ]
class SlurpitIPAddressSerializer(
    RelationshipModelSerializerMixin, CustomFieldModelSerializerMixin, ValidatedModelSerializer
):
    address = IPFieldSerializer()
    class Meta:
        model = SlurpitIPAddress
        fields = [
            'id', 'address', 'namespace', 'type', 'status', 'role',
            'dns_name', 'description', 'custom_fields', 'created', 'last_updated',
        ]