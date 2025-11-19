"""Filtersets for FreeIPA models."""

import django_filters
from netbox.filtersets import NetBoxModelFilterSet

from .models import FreeIPAHost, FreeIPADNSZone, FreeIPADNSRecord


class FreeIPAHostFilterSet(NetBoxModelFilterSet):
    """Filterset for FreeIPA hosts."""
    
    fqdn = django_filters.CharFilter(
        field_name='fqdn',
        lookup_expr='icontains',
        label='FQDN'
    )
    
    class Meta:
        model = FreeIPAHost
        fields = ['id', 'fqdn', 'description', 'ipa_uuid', 'managed_by']


class FreeIPADNSZoneFilterSet(NetBoxModelFilterSet):
    """Filterset for FreeIPA DNS zones."""
    
    zone_name = django_filters.CharFilter(
        field_name='zone_name',
        lookup_expr='icontains',
        label='Zone Name'
    )
    
    zone_type = django_filters.CharFilter(
        field_name='zone_type',
        lookup_expr='iexact',
        label='Zone Type'
    )
    
    dynamic_update = django_filters.BooleanFilter(
        field_name='dynamic_update',
        label='Dynamic Update'
    )
    
    class Meta:
        model = FreeIPADNSZone
        fields = [
            'id', 'zone_name', 'zone_type', 'dynamic_update', 'allow_sync_ptr'
        ]


class FreeIPADNSRecordFilterSet(NetBoxModelFilterSet):
    """Filterset for FreeIPA DNS records."""
    
    dns_zone_id = django_filters.ModelMultipleChoiceFilter(
        queryset=FreeIPADNSZone.objects.all(),
        label='DNS Zone',
    )
    
    record_name = django_filters.CharFilter(
        field_name='record_name',
        lookup_expr='icontains',
        label='Record Name'
    )
    
    record_type = django_filters.MultipleChoiceFilter(
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
    
    record_value = django_filters.CharFilter(
        field_name='record_value',
        lookup_expr='icontains',
        label='Record Value'
    )
    
    host_id = django_filters.ModelMultipleChoiceFilter(
        queryset=FreeIPAHost.objects.all(),
        label='Host',
    )
    
    class Meta:
        model = FreeIPADNSRecord
        fields = [
            'id', 'dns_zone_id', 'record_name', 'record_type',
            'record_value', 'host_id'
        ]
