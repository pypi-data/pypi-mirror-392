"""NetBox FreeIPA Plugin - Integration with FreeIPA identity management."""

from netbox.plugins import PluginConfig

__version__ = '0.2.7'


class NetBoxFreeIPAConfig(PluginConfig):
    """Plugin configuration for NetBox FreeIPA integration."""
    
    name = 'netbox_freeipa'
    verbose_name = 'NetBox FreeIPA Integration'
    description = 'Integration with FreeIPA identity management - hosts, DNS zones and records'
    version = __version__
    author = 'Maksym Hrytsaienko'
    author_email = 'hrytsaienko.my@gmail.com'
    base_url = 'freeipa'
    min_version = '4.0.0'
    max_version = '4.12.0'
    
    # Required settings that must be defined by the user
    required_settings = [
        'freeipa_host',
        'freeipa_username',
        'freeipa_password',
    ]
    
    # Default settings
    default_settings = {
        'freeipa_verify_ssl': True,
        'freeipa_ca_cert': None,
        'sync_interval': 300,  # seconds
        'page_size': 100,
        'auto_sync_enabled': True,  # Enable automatic background sync
    }
    
    # Background jobs for automatic synchronization
    queues = ['default']


config = NetBoxFreeIPAConfig
