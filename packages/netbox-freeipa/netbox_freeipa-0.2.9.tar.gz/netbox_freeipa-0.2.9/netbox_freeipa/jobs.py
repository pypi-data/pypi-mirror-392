"""Background jobs for NetBox FreeIPA plugin."""

import logging
from core.choices import JobIntervalChoices
from netbox.jobs import JobRunner, system_job
from netbox.plugins import get_plugin_config

logger = logging.getLogger('netbox.plugins.netbox_freeipa')


# Get sync interval and convert from seconds to minutes
# Default is 300 seconds (5 minutes)
def get_sync_interval_minutes():
    """Get sync interval from config and convert to minutes."""
    try:
        interval_seconds = get_plugin_config('netbox_freeipa', 'sync_interval', 300)
        return max(1, interval_seconds // 60)  # Minimum 1 minute
    except Exception:
        return 5  # Default to 5 minutes if config not available


@system_job(interval=get_sync_interval_minutes())
class SyncFreeIPADataJob(JobRunner):
    """
    System job to automatically synchronize all FreeIPA data with NetBox.
    
    This job runs automatically based on the sync_interval configuration.
    Synchronizes hosts, DNS zones, and DNS records from FreeIPA.
    """
    
    class Meta:
        name = 'Sync FreeIPA Data'
    
    def run(self, *args, **kwargs):
        """
        Execute the synchronization job.
        
        This method synchronizes all data types: hosts, DNS zones, and DNS records.
        """
        from .freeipa_client import FreeIPAClient
        
        self.logger.info("Starting FreeIPA full synchronization")
        
        try:
            client = FreeIPAClient()
            results = client.sync_all()
            
            # Log results for each entity type
            for entity_type, stats in results.items():
                if 'error' in stats:
                    self.logger.error(
                        f"{entity_type} synchronization failed: {stats['error']}"
                    )
                else:
                    self.logger.info(
                        f"{entity_type}: {stats['created']} created, "
                        f"{stats['updated']} updated, {stats['deleted']} deleted"
                    )
                    
                    if stats.get('errors', 0) > 0:
                        self.logger.warning(
                            f"{entity_type}: {stats['errors']} errors occurred"
                        )
            
            # Calculate totals
            total_created = sum(s.get('created', 0) for s in results.values() if 'error' not in s)
            total_updated = sum(s.get('updated', 0) for s in results.values() if 'error' not in s)
            total_deleted = sum(s.get('deleted', 0) for s in results.values() if 'error' not in s)
            total_errors = sum(s.get('errors', 0) for s in results.values() if 'error' not in s)
            
            self.logger.info(
                f"Full synchronization completed: "
                f"Total: {total_created} created, {total_updated} updated, "
                f"{total_deleted} deleted, {total_errors} errors"
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Full synchronization failed: {str(e)}")
            raise
