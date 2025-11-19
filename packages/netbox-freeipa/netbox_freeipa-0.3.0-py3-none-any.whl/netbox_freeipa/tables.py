"""Tables for displaying FreeIPA data in NetBox."""

import django_tables2 as tables
from netbox.tables import NetBoxTable, columns

from .models import FreeIPAHost, FreeIPADNSZone, FreeIPADNSRecord


class FreeIPAHostTable(NetBoxTable):
    """Table for displaying FreeIPA hosts."""
    
    fqdn = tables.Column(
        linkify=True,
        verbose_name='FQDN'
    )
    
    dns_records = tables.Column(
        accessor='dns_records.count',
        verbose_name='DNS Records',
        orderable=False
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
            'pk', 'fqdn', 'description', 'ipa_uuid', 'dns_records',
            'managed_by', 'last_synced', 'actions'
        )
        default_columns = (
            'pk', 'fqdn', 'description', 'dns_records', 'last_synced'
        )


class FreeIPADNSZoneTable(NetBoxTable):
    """Table for displaying FreeIPA DNS zones."""
    
    zone_name = tables.Column(
        linkify=True,
        verbose_name='Zone Name'
    )
    
    zone_type = tables.Column(
        verbose_name='Type'
    )
    
    dns_records = tables.Column(
        accessor='dns_records.count',
        verbose_name='Records',
        orderable=False
    )
    
    serial_number = tables.Column(
        verbose_name='Serial'
    )
    
    dynamic_update = columns.BooleanColumn(
        verbose_name='Dynamic'
    )
    
    last_synced = columns.DateTimeColumn(
        verbose_name='Last Synced'
    )
    
    actions = columns.ActionsColumn(
        actions=('edit', 'delete')
    )
    
    class Meta(NetBoxTable.Meta):
        model = FreeIPADNSZone
        fields = (
            'pk', 'zone_name', 'zone_type', 'authoritative_nameserver',
            'dns_records', 'serial_number', 'ttl', 'dynamic_update',
            'last_synced', 'actions'
        )
        default_columns = (
            'pk', 'zone_name', 'zone_type', 'dns_records', 'serial_number',
            'last_synced'
        )


class FreeIPADNSRecordTable(NetBoxTable):
    """Table for displaying FreeIPA DNS records."""
    
    dns_zone = tables.Column(
        linkify=True,
        verbose_name='Zone',
        accessor='dns_zone.zone_name'
    )
    
    record_name = tables.Column(
        linkify=True,
        verbose_name='Name'
    )
    
    record_type = tables.Column(
        verbose_name='Type'
    )
    
    record_value = tables.Column(
        verbose_name='Value'
    )
    
    host = tables.Column(
        linkify=True,
        verbose_name='Host',
        accessor='host.fqdn'
    )
    
    fqdn = tables.Column(
        verbose_name='FQDN',
        orderable=False
    )
    
    last_synced = columns.DateTimeColumn(
        verbose_name='Last Synced'
    )
    
    actions = columns.ActionsColumn(
        actions=('edit', 'delete')
    )
    
    class Meta(NetBoxTable.Meta):
        model = FreeIPADNSRecord
        fields = (
            'pk', 'dns_zone', 'record_name', 'fqdn', 'record_type',
            'record_value', 'ttl', 'host', 'last_synced', 'actions'
        )
        default_columns = (
            'pk', 'dns_zone', 'record_name', 'record_type', 'record_value',
            'host'
        )
