"""REST API serializers for NetBox FreeIPA plugin."""

from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer

from ..models import FreeIPAHost, FreeIPADNSZone, FreeIPADNSRecord

__all__ = (
    'FreeIPAHostSerializer',
    'FreeIPADNSZoneSerializer',
    'FreeIPADNSRecordSerializer',
)


class FreeIPAHostSerializer(NetBoxModelSerializer):
    """Serializer for FreeIPAHost model."""
    
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_freeipa-api:freeipahost-detail'
    )
    
    display = serializers.SerializerMethodField()
    dns_records_count = serializers.SerializerMethodField()
    
    class Meta:
        model = FreeIPAHost
        fields = [
            'id', 'url', 'display', 'fqdn', 'description', 'ipa_uuid',
            'ssh_public_key', 'managed_by', 'last_synced', 'dns_records_count',
            'tags', 'created', 'last_updated', 'custom_fields',
        ]
        brief_fields = ['id', 'url', 'display', 'fqdn']
    
    def get_display(self, obj):
        """Return display representation."""
        return str(obj)
    
    def get_dns_records_count(self, obj):
        """Return count of associated DNS records."""
        return obj.dns_records.count()


class FreeIPADNSZoneSerializer(NetBoxModelSerializer):
    """Serializer for FreeIPADNSZone model."""
    
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_freeipa-api:freeipadnszone-detail'
    )
    
    display = serializers.SerializerMethodField()
    dns_records_count = serializers.SerializerMethodField()
    
    class Meta:
        model = FreeIPADNSZone
        fields = [
            'id', 'url', 'display', 'zone_name', 'zone_type',
            'authoritative_nameserver', 'administrator_email', 'serial_number',
            'refresh', 'retry', 'expire', 'minimum', 'ttl', 'dynamic_update',
            'allow_sync_ptr', 'last_synced', 'dns_records_count',
            'tags', 'created', 'last_updated', 'custom_fields',
        ]
        brief_fields = ['id', 'url', 'display', 'zone_name', 'zone_type']
    
    def get_display(self, obj):
        """Return display representation."""
        return str(obj)
    
    def get_dns_records_count(self, obj):
        """Return count of DNS records in this zone."""
        return obj.dns_records.count()


class FreeIPADNSRecordSerializer(NetBoxModelSerializer):
    """Serializer for FreeIPADNSRecord model."""
    
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_freeipa-api:freeipadnsrecord-detail'
    )
    
    dns_zone = serializers.SerializerMethodField()
    host = serializers.SerializerMethodField()
    display = serializers.SerializerMethodField()
    fqdn = serializers.CharField(read_only=True)
    
    class Meta:
        model = FreeIPADNSRecord
        fields = [
            'id', 'url', 'display', 'dns_zone', 'record_name', 'record_type',
            'record_value', 'ttl', 'host', 'fqdn', 'last_synced',
            'tags', 'created', 'last_updated', 'custom_fields',
        ]
        brief_fields = ['id', 'url', 'display', 'record_name', 'record_type', 'record_value']
    
    def get_display(self, obj):
        """Return display representation."""
        return str(obj)
    
    def get_dns_zone(self, obj):
        """Return brief zone information."""
        if obj.dns_zone:
            zone_data = {
                'id': obj.dns_zone.id,
                'zone_name': obj.dns_zone.zone_name,
            }
            # Only build URL if request context is available
            request = self.context.get('request')
            if request:
                zone_data['url'] = request.build_absolute_uri(
                    obj.dns_zone.get_absolute_url()
                )
            return zone_data
        return None
    
    def get_host(self, obj):
        """Return brief host information if associated."""
        if obj.host:
            host_data = {
                'id': obj.host.id,
                'fqdn': obj.host.fqdn,
            }
            # Only build URL if request context is available
            request = self.context.get('request')
            if request:
                host_data['url'] = request.build_absolute_uri(
                    obj.host.get_absolute_url()
                )
            return host_data
        return None
