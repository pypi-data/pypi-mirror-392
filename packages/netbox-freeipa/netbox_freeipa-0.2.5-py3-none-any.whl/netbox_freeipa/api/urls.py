"""REST API URL configuration for NetBox FreeIPA plugin."""

from netbox.api.routers import NetBoxRouter

from .views import (
    FreeIPAHostViewSet,
    FreeIPADNSZoneViewSet,
    FreeIPADNSRecordViewSet,
    FreeIPASyncViewSet,
)


router = NetBoxRouter()
router.register('hosts', FreeIPAHostViewSet)
router.register('dns-zones', FreeIPADNSZoneViewSet)
router.register('dns-records', FreeIPADNSRecordViewSet)
router.register('sync', FreeIPASyncViewSet, basename='sync')

urlpatterns = router.urls
