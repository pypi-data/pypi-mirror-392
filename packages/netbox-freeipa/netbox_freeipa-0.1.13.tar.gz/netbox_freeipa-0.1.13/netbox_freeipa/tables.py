"""Tables for displaying FreeIPA data in NetBox."""

import django_tables2 as tables
from netbox.tables import NetBoxTable, columns

from .models import FreeIPAHost


class FreeIPAHostTable(NetBoxTable):
    """Table for displaying FreeIPA hosts."""
    
    fqdn = tables.Column(
        linkify=True,
        verbose_name='FQDN'
    )
    
    enrolled = columns.BooleanColumn(
        verbose_name='Enrolled'
    )
    
    ip_address = tables.Column(
        verbose_name='IP Address'
    )
    
    mac_address = tables.Column(
        verbose_name='MAC Address'
    )
    
    has_keytab = columns.BooleanColumn(
        verbose_name='Has Keytab'
    )
    
    enrollment_date = columns.DateTimeColumn(
        verbose_name='Enrolled On'
    )
    
    last_synced = columns.DateTimeColumn(
        verbose_name='Last Synced'
    )
    
    actions = columns.ActionsColumn(
        actions=('edit', 'delete')
    )
    
    class Meta(NetBoxTable.Meta):
        model = FreeIPAHost
        fields = (
            'pk', 'fqdn', 'description', 'enrolled', 'ip_address',
            'mac_address', 'has_keytab', 'enrollment_date', 'last_synced',
            'actions'
        )
        default_columns = (
            'pk', 'fqdn', 'description', 'enrolled', 'ip_address',
            'has_keytab', 'enrollment_date'
        )
