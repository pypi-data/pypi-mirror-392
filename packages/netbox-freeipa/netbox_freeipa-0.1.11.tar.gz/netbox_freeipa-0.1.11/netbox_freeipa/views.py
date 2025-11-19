"""Views for NetBox FreeIPA plugin."""

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from netbox.views import generic

from .models import FreeIPAHost
from .tables import FreeIPAHostTable
from .filtersets import FreeIPAHostFilterSet
from .forms import FreeIPAHostFilterForm
from .freeipa_client import FreeIPAClient


class FreeIPAHostListView(generic.ObjectListView):
    """List view for FreeIPA hosts."""
    
    queryset = FreeIPAHost.objects.all()
    table = FreeIPAHostTable
    filterset = FreeIPAHostFilterSet
    filterset_form = FreeIPAHostFilterForm
    template_name = 'netbox_freeipa/freeipahost_list.html'


class FreeIPAHostView(generic.ObjectView):
    """Detail view for a single FreeIPA host."""
    
    queryset = FreeIPAHost.objects.all()
    template_name = 'netbox_freeipa/freeipahost.html'


class FreeIPAHostEditView(generic.ObjectEditView):
    """Edit view for FreeIPA host."""
    
    queryset = FreeIPAHost.objects.all()
    template_name = 'netbox_freeipa/freeipahost_edit.html'


class FreeIPAHostDeleteView(generic.ObjectDeleteView):
    """Delete view for FreeIPA host."""
    
    queryset = FreeIPAHost.objects.all()


class FreeIPAHostBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for FreeIPA hosts."""
    
    queryset = FreeIPAHost.objects.all()
    table = FreeIPAHostTable


class FreeIPASyncView(View):
    """View to trigger synchronization with FreeIPA server."""
    
    def post(self, request):
        """Handle POST request to sync with FreeIPA."""
        try:
            client = FreeIPAClient()
            stats = client.sync_hosts()
            
            messages.success(
                request,
                f"Synchronization completed successfully: "
                f"{stats['created']} created, "
                f"{stats['updated']} updated, "
                f"{stats['deleted']} deleted"
            )
            
            if stats['errors'] > 0:
                messages.warning(
                    request,
                    f"{stats['errors']} errors occurred during synchronization"
                )
        
        except Exception as e:
            messages.error(
                request,
                f"Synchronization failed: {str(e)}"
            )
        
        return redirect('plugins:netbox_freeipa:freeipahost_list')
    
    def get(self, request):
        """Handle GET request to show sync confirmation page."""
        return render(
            request,
            'netbox_freeipa/freeipahost_sync.html'
        )
