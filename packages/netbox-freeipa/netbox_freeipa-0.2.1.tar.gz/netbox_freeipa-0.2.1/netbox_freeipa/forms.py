"""Django forms for NetBox FreeIPA plugin."""

from django import forms
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import DynamicModelChoiceField, DynamicModelMultipleChoiceField

from .models import FreeIPAHost, FreeIPADNSZone, FreeIPADNSRecord


class FreeIPAHostForm(NetBoxModelForm):
    """Form for creating/editing FreeIPA hosts."""
    
    class Meta:
        model = FreeIPAHost
        fields = [
            'fqdn', 'description', 'ipa_uuid', 'ssh_public_key',
            'managed_by', 'tags'
        ]


class FreeIPAHostFilterForm(NetBoxModelFilterSetForm):
    """Filter form for FreeIPA hosts list."""
    
    model = FreeIPAHost
    
    fqdn = forms.CharField(
        required=False,
        label='FQDN'
    )


class FreeIPADNSZoneForm(NetBoxModelForm):
    """Form for creating/editing FreeIPA DNS zones."""
    
    class Meta:
        model = FreeIPADNSZone
        fields = [
            'zone_name', 'zone_type', 'authoritative_nameserver',
            'administrator_email', 'serial_number', 'refresh', 'retry',
            'expire', 'minimum', 'ttl', 'dynamic_update', 'allow_sync_ptr',
            'tags'
        ]


class FreeIPADNSZoneFilterForm(NetBoxModelFilterSetForm):
    """Filter form for FreeIPA DNS zones list."""
    
    model = FreeIPADNSZone
    
    zone_name = forms.CharField(
        required=False,
        label='Zone Name'
    )
    
    zone_type = forms.CharField(
        required=False,
        label='Zone Type'
    )
    
    dynamic_update = forms.NullBooleanField(
        required=False,
        label='Dynamic Update',
        widget=forms.Select(choices=(
            ('', '---------'),
            ('true', 'Yes'),
            ('false', 'No'),
        ))
    )


class FreeIPADNSRecordForm(NetBoxModelForm):
    """Form for creating/editing FreeIPA DNS records."""
    
    dns_zone = DynamicModelChoiceField(
        queryset=FreeIPADNSZone.objects.all(),
        label='DNS Zone'
    )
    
    host = DynamicModelChoiceField(
        queryset=FreeIPAHost.objects.all(),
        required=False,
        label='Associated Host'
    )
    
    class Meta:
        model = FreeIPADNSRecord
        fields = [
            'dns_zone', 'record_name', 'record_type', 'record_value',
            'ttl', 'host', 'tags'
        ]


class FreeIPADNSRecordFilterForm(NetBoxModelFilterSetForm):
    """Filter form for FreeIPA DNS records list."""
    
    model = FreeIPADNSRecord
    
    dns_zone_id = DynamicModelMultipleChoiceField(
        queryset=FreeIPADNSZone.objects.all(),
        required=False,
        label='DNS Zone'
    )
    
    record_name = forms.CharField(
        required=False,
        label='Record Name'
    )
    
    record_type = forms.MultipleChoiceField(
        required=False,
        choices=[
            ('A', 'A'),
            ('AAAA', 'AAAA'),
            ('CNAME', 'CNAME'),
            ('MX', 'MX'),
            ('PTR', 'PTR'),
            ('TXT', 'TXT'),
            ('SRV', 'SRV'),
        ],
        label='Record Type'
    )
    
    record_value = forms.CharField(
        required=False,
        label='Record Value'
    )
    
    host_id = DynamicModelMultipleChoiceField(
        queryset=FreeIPAHost.objects.all(),
        required=False,
        label='Host'
    )
