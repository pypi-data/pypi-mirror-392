"""Views for NetBox FreeIPA plugin."""

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from netbox.views import generic

from .models import FreeIPAHost, FreeIPADNSZone, FreeIPADNSRecord
from .tables import FreeIPAHostTable, FreeIPADNSZoneTable, FreeIPADNSRecordTable
from .filtersets import FreeIPAHostFilterSet, FreeIPADNSZoneFilterSet, FreeIPADNSRecordFilterSet
from .forms import (
    FreeIPAHostFilterForm, FreeIPAHostForm,
    FreeIPADNSZoneFilterForm, FreeIPADNSZoneForm,
    FreeIPADNSRecordFilterForm, FreeIPADNSRecordForm,
)
from .freeipa_client import FreeIPAClient


# Host Views
class FreeIPAHostListView(generic.ObjectListView):
    """List view for FreeIPA hosts."""
    
    queryset = FreeIPAHost.objects.prefetch_related('dns_records')
    table = FreeIPAHostTable
    filterset = FreeIPAHostFilterSet
    filterset_form = FreeIPAHostFilterForm
    template_name = 'netbox_freeipa/freeipahost_list.html'


class FreeIPAHostView(generic.ObjectView):
    """Detail view for a single FreeIPA host."""
    
    queryset = FreeIPAHost.objects.prefetch_related('dns_records')
    template_name = 'netbox_freeipa/freeipahost.html'


class FreeIPAHostEditView(generic.ObjectEditView):
    """Edit view for FreeIPA host."""
    
    queryset = FreeIPAHost.objects.all()
    form = FreeIPAHostForm
    template_name = 'netbox_freeipa/freeipahost_edit.html'


class FreeIPAHostDeleteView(generic.ObjectDeleteView):
    """Delete view for FreeIPA host."""
    
    queryset = FreeIPAHost.objects.all()


class FreeIPAHostBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for FreeIPA hosts."""
    
    queryset = FreeIPAHost.objects.all()
    table = FreeIPAHostTable


# DNS Zone Views
class FreeIPADNSZoneListView(generic.ObjectListView):
    """List view for FreeIPA DNS zones."""
    
    queryset = FreeIPADNSZone.objects.prefetch_related('dns_records')
    table = FreeIPADNSZoneTable
    filterset = FreeIPADNSZoneFilterSet
    filterset_form = FreeIPADNSZoneFilterForm
    template_name = 'netbox_freeipa/freeipadnszone_list.html'


class FreeIPADNSZoneView(generic.ObjectView):
    """Detail view for a single FreeIPA DNS zone."""
    
    queryset = FreeIPADNSZone.objects.prefetch_related('dns_records')
    template_name = 'netbox_freeipa/freeipadnszone.html'


class FreeIPADNSZoneEditView(generic.ObjectEditView):
    """Edit view for FreeIPA DNS zone."""
    
    queryset = FreeIPADNSZone.objects.all()
    form = FreeIPADNSZoneForm
    template_name = 'netbox_freeipa/freeipadnszone_edit.html'


class FreeIPADNSZoneDeleteView(generic.ObjectDeleteView):
    """Delete view for FreeIPA DNS zone."""
    
    queryset = FreeIPADNSZone.objects.all()


class FreeIPADNSZoneBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for FreeIPA DNS zones."""
    
    queryset = FreeIPADNSZone.objects.all()
    table = FreeIPADNSZoneTable


# DNS Record Views
class FreeIPADNSRecordListView(generic.ObjectListView):
    """List view for FreeIPA DNS records."""
    
    queryset = FreeIPADNSRecord.objects.select_related('dns_zone', 'host')
    table = FreeIPADNSRecordTable
    filterset = FreeIPADNSRecordFilterSet
    filterset_form = FreeIPADNSRecordFilterForm
    template_name = 'netbox_freeipa/freeipadnsrecord_list.html'


class FreeIPADNSRecordView(generic.ObjectView):
    """Detail view for a single FreeIPA DNS record."""
    
    queryset = FreeIPADNSRecord.objects.select_related('dns_zone', 'host')
    template_name = 'netbox_freeipa/freeipadnsrecord.html'


class FreeIPADNSRecordEditView(generic.ObjectEditView):
    """Edit view for FreeIPA DNS record."""
    
    queryset = FreeIPADNSRecord.objects.all()
    form = FreeIPADNSRecordForm
    template_name = 'netbox_freeipa/freeipadnsrecord_edit.html'


class FreeIPADNSRecordDeleteView(generic.ObjectDeleteView):
    """Delete view for FreeIPA DNS record."""
    
    queryset = FreeIPADNSRecord.objects.all()


class FreeIPADNSRecordBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for FreeIPA DNS records."""
    
    queryset = FreeIPADNSRecord.objects.all()
    table = FreeIPADNSRecordTable


# Synchronization View
class FreeIPASyncView(View):
    """View to trigger synchronization with FreeIPA server."""
    
    def post(self, request):
        """Handle POST request to sync with FreeIPA."""
        sync_type = request.POST.get('sync_type', 'all')
        
        try:
            client = FreeIPAClient()
            
            if sync_type == 'hosts':
                stats = client.sync_hosts()
                messages.success(
                    request,
                    f"Host synchronization completed: "
                    f"{stats['created']} created, "
                    f"{stats['updated']} updated, "
                    f"{stats['deleted']} deleted"
                )
            elif sync_type == 'dns_zones':
                stats = client.sync_dns_zones()
                messages.success(
                    request,
                    f"DNS zone synchronization completed: "
                    f"{stats['created']} created, "
                    f"{stats['updated']} updated, "
                    f"{stats['deleted']} deleted"
                )
            elif sync_type == 'dns_records':
                stats = client.sync_dns_records()
                messages.success(
                    request,
                    f"DNS record synchronization completed: "
                    f"{stats['created']} created, "
                    f"{stats['updated']} updated, "
                    f"{stats['deleted']} deleted"
                )
            else:  # all
                results = client.sync_all()
                
                # Display results for each entity type
                for entity_type, stats in results.items():
                    if 'error' in stats:
                        messages.error(
                            request,
                            f"{entity_type} synchronization failed: {stats['error']}"
                        )
                    else:
                        messages.success(
                            request,
                            f"{entity_type}: {stats['created']} created, "
                            f"{stats['updated']} updated, {stats['deleted']} deleted"
                        )
            
            if any(stats.get('errors', 0) > 0 for stats in 
                   (results.values() if sync_type == 'all' else [stats])):
                messages.warning(
                    request,
                    "Some errors occurred during synchronization. Check logs for details."
                )
        
        except Exception as e:
            messages.error(
                request,
                f"Synchronization failed: {str(e)}"
            )
        
        return redirect('plugins:netbox_freeipa:freeipahost_sync')
    
    def get(self, request):
        """Handle GET request to show sync confirmation page."""
        return render(
            request,
            'netbox_freeipa/freeipahost_sync.html'
        )
