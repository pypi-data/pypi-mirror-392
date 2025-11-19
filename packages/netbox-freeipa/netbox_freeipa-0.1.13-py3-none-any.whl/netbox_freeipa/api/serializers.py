"""REST API serializers for NetBox FreeIPA plugin."""

from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer

from ..models import FreeIPAHost

__all__ = ('FreeIPAHostSerializer',)


class FreeIPAHostSerializer(NetBoxModelSerializer):
    """Serializer for FreeIPAHost model."""
    
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_freeipa-api:freeipahost-detail'
    )
    
    display = serializers.SerializerMethodField()
    status_label = serializers.CharField(read_only=True)
    is_certificate_valid = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = FreeIPAHost
        fields = [
            'id', 'url', 'display', 'fqdn', 'description', 'enrolled',
            'enrollment_date', 'ipa_uuid', 'mac_address', 'ip_address',
            'ssh_public_key', 'has_keytab', 'certificate_subject',
            'certificate_issuer', 'certificate_valid_not_before',
            'certificate_valid_not_after', 'managed_by', 'last_synced',
            'status_label', 'is_certificate_valid', 'tags', 'created',
            'last_updated', 'custom_fields',
        ]
        brief_fields = ['id', 'url', 'display', 'fqdn', 'enrolled']
    
    def get_display(self, obj):
        """Return display representation."""
        return str(obj)
