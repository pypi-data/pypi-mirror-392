"""Admin configuration for NetBox FreeIPA plugin models."""

from django.contrib import admin

from .models import FreeIPAHost


@admin.register(FreeIPAHost)
class FreeIPAHostAdmin(admin.ModelAdmin):
    """Admin interface for FreeIPAHost model."""
    
    list_display = [
        'fqdn', 'enrolled', 'ip_address', 'mac_address',
        'has_keytab', 'enrollment_date', 'last_synced'
    ]
    
    list_filter = [
        'enrolled', 'has_keytab', 'enrollment_date'
    ]
    
    search_fields = [
        'fqdn', 'description', 'ip_address', 'mac_address', 'ipa_uuid'
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
        ('Enrollment', {
            'fields': (
                'enrolled', 'enrollment_date', 'has_keytab'
            )
        }),
        ('Network', {
            'fields': (
                'ip_address', 'mac_address'
            )
        }),
        ('Authentication', {
            'fields': (
                'ssh_public_key',
            )
        }),
        ('Certificate', {
            'fields': (
                'certificate_subject', 'certificate_issuer',
                'certificate_valid_not_before', 'certificate_valid_not_after'
            )
        }),
        ('Metadata', {
            'fields': (
                'last_synced', 'tags'
            )
        }),
    )
