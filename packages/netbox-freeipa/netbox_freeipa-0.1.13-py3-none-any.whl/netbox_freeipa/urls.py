"""URL configuration for NetBox FreeIPA plugin."""

from django.urls import path

from . import views


urlpatterns = [
    # Host list and detail views
    path('hosts/', views.FreeIPAHostListView.as_view(), name='freeipahost_list'),
    path('hosts/<int:pk>/', views.FreeIPAHostView.as_view(), name='freeipahost'),
    path('hosts/<int:pk>/edit/', views.FreeIPAHostEditView.as_view(), name='freeipahost_edit'),
    path('hosts/<int:pk>/delete/', views.FreeIPAHostDeleteView.as_view(), name='freeipahost_delete'),
    path('hosts/delete/', views.FreeIPAHostBulkDeleteView.as_view(), name='freeipahost_bulk_delete'),
    
    # Synchronization view
    path('sync/', views.FreeIPASyncView.as_view(), name='freeipahost_sync'),
]
