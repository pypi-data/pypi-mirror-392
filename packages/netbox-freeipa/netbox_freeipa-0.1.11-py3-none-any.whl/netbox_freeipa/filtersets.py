"""Filtersets for FreeIPA models."""

import django_filters
from netbox.filtersets import NetBoxModelFilterSet

from .models import FreeIPAHost


class FreeIPAHostFilterSet(NetBoxModelFilterSet):
    """Filterset for FreeIPA hosts."""
    
    fqdn = django_filters.CharFilter(
        field_name='fqdn',
        lookup_expr='icontains',
        label='FQDN'
    )
    
    enrolled = django_filters.BooleanFilter(
        field_name='enrolled',
        label='Enrolled'
    )
    
    has_keytab = django_filters.BooleanFilter(
        field_name='has_keytab',
        label='Has Keytab'
    )
    
    ip_address = django_filters.CharFilter(
        field_name='ip_address',
        lookup_expr='icontains',
        label='IP Address'
    )
    
    mac_address = django_filters.CharFilter(
        field_name='mac_address',
        lookup_expr='icontains',
        label='MAC Address'
    )
    
    class Meta:
        model = FreeIPAHost
        fields = [
            'id', 'fqdn', 'description', 'enrolled', 'has_keytab',
            'ip_address', 'mac_address'
        ]
