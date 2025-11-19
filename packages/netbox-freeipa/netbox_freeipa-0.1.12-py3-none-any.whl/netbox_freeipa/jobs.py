"""Background jobs for NetBox FreeIPA plugin."""

from datetime import timedelta
from django.utils import timezone

from netbox.plugins import get_plugin_config
from .freeipa_client import FreeIPAClient


def sync_freeipa_hosts(job):
    """
    Background job to synchronize FreeIPA hosts with NetBox.
    
    This job runs automatically based on the sync_interval configuration.
    """
    job.log_info("Starting FreeIPA synchronization")
    
    try:
        client = FreeIPAClient()
        stats = client.sync_hosts()
        
        job.log_success(
            f"Synchronization completed: "
            f"{stats['created']} created, "
            f"{stats['updated']} updated, "
            f"{stats['deleted']} deleted"
        )
        
        if stats['errors'] > 0:
            job.log_warning(f"{stats['errors']} errors occurred during synchronization")
        
        return stats
        
    except Exception as e:
        job.log_failure(f"Synchronization failed: {str(e)}")
        raise


# Job configuration
jobs = [
    {
        'name': 'Sync FreeIPA Hosts',
        'func': sync_freeipa_hosts,
        'interval': get_plugin_config('netbox_freeipa', 'sync_interval', 300),
        'description': 'Synchronize enrolled hosts from FreeIPA server',
    }
]
