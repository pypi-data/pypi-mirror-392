"""Admin configuration for NetBox FreeIPA plugin models."""

from django.contrib import admin

from .models import FreeIPAHost, FreeIPADNSZone, FreeIPADNSRecord


@admin.register(FreeIPAHost)
class FreeIPAHostAdmin(admin.ModelAdmin):
    """Admin interface for FreeIPAHost model."""
    
    list_display = [
        'fqdn', 'ipa_uuid', 'managed_by', 'last_synced'
    ]
    
    list_filter = [
        'last_synced',
    ]
    
    search_fields = [
        'fqdn', 'description', 'ipa_uuid', 'managed_by'
    ]
    
    readonly_fields = [
        'last_synced', 'created', 'last_updated'
    ]
    
    fieldsets = (
        ('Host Information', {
            'fields': (
                'fqdn', 'description', 'ipa_uuid', 'managed_by'
            )
        }),
        ('Authentication', {
            'fields': (
                'ssh_public_key',
            )
        }),
        ('Metadata', {
            'fields': (
                'last_synced', 'tags'
            )
        }),
    )


@admin.register(FreeIPADNSZone)
class FreeIPADNSZoneAdmin(admin.ModelAdmin):
    """Admin interface for FreeIPADNSZone model."""
    
    list_display = [
        'zone_name', 'zone_type', 'serial_number', 'dynamic_update', 'last_synced'
    ]
    
    list_filter = [
        'zone_type', 'dynamic_update', 'allow_sync_ptr', 'last_synced'
    ]
    
    search_fields = [
        'zone_name', 'authoritative_nameserver', 'administrator_email'
    ]
    
    readonly_fields = [
        'last_synced', 'created', 'last_updated'
    ]
    
    fieldsets = (
        ('Zone Information', {
            'fields': (
                'zone_name', 'zone_type', 'authoritative_nameserver',
                'administrator_email'
            )
        }),
        ('SOA Record', {
            'fields': (
                'serial_number', 'refresh', 'retry', 'expire', 'minimum'
            )
        }),
        ('Settings', {
            'fields': (
                'ttl', 'dynamic_update', 'allow_sync_ptr'
            )
        }),
        ('Metadata', {
            'fields': (
                'last_synced', 'tags'
            )
        }),
    )


@admin.register(FreeIPADNSRecord)
class FreeIPADNSRecordAdmin(admin.ModelAdmin):
    """Admin interface for FreeIPADNSRecord model."""
    
    list_display = [
        'record_name', 'dns_zone', 'record_type', 'record_value', 'host', 'last_synced'
    ]
    
    list_filter = [
        'record_type', 'dns_zone', 'last_synced'
    ]
    
    search_fields = [
        'record_name', 'record_value', 'dns_zone__zone_name', 'host__fqdn'
    ]
    
    readonly_fields = [
        'fqdn', 'last_synced', 'created', 'last_updated'
    ]
    
    fieldsets = (
        ('Record Information', {
            'fields': (
                'dns_zone', 'record_name', 'fqdn', 'record_type', 'record_value', 'ttl'
            )
        }),
        ('Association', {
            'fields': (
                'host',
            )
        }),
        ('Metadata', {
            'fields': (
                'last_synced', 'tags'
            )
        }),
    )
