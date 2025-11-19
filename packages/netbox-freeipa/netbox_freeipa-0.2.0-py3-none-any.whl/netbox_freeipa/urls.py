"""URL configuration for NetBox FreeIPA plugin."""

from django.urls import path

from . import views


urlpatterns = [
    # Host URLs
    path('hosts/', views.FreeIPAHostListView.as_view(), name='freeipahost_list'),
    path('hosts/<int:pk>/', views.FreeIPAHostView.as_view(), name='freeipahost'),
    path('hosts/<int:pk>/edit/', views.FreeIPAHostEditView.as_view(), name='freeipahost_edit'),
    path('hosts/<int:pk>/delete/', views.FreeIPAHostDeleteView.as_view(), name='freeipahost_delete'),
    path('hosts/delete/', views.FreeIPAHostBulkDeleteView.as_view(), name='freeipahost_bulk_delete'),
    
    # DNS Zone URLs
    path('dns-zones/', views.FreeIPADNSZoneListView.as_view(), name='freeipadnszone_list'),
    path('dns-zones/<int:pk>/', views.FreeIPADNSZoneView.as_view(), name='freeipadnszone'),
    path('dns-zones/<int:pk>/edit/', views.FreeIPADNSZoneEditView.as_view(), name='freeipadnszone_edit'),
    path('dns-zones/<int:pk>/delete/', views.FreeIPADNSZoneDeleteView.as_view(), name='freeipadnszone_delete'),
    path('dns-zones/delete/', views.FreeIPADNSZoneBulkDeleteView.as_view(), name='freeipadnszone_bulk_delete'),
    
    # DNS Record URLs
    path('dns-records/', views.FreeIPADNSRecordListView.as_view(), name='freeipadnsrecord_list'),
    path('dns-records/<int:pk>/', views.FreeIPADNSRecordView.as_view(), name='freeipadnsrecord'),
    path('dns-records/<int:pk>/edit/', views.FreeIPADNSRecordEditView.as_view(), name='freeipadnsrecord_edit'),
    path('dns-records/<int:pk>/delete/', views.FreeIPADNSRecordDeleteView.as_view(), name='freeipadnsrecord_delete'),
    path('dns-records/delete/', views.FreeIPADNSRecordBulkDeleteView.as_view(), name='freeipadnsrecord_bulk_delete'),
    
    # Synchronization URL
    path('sync/', views.FreeIPASyncView.as_view(), name='freeipahost_sync'),
]
