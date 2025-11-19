"""REST API URL configuration for NetBox FreeIPA plugin."""

from netbox.api.routers import NetBoxRouter

from .views import FreeIPAHostViewSet


router = NetBoxRouter()
router.register('hosts', FreeIPAHostViewSet)

urlpatterns = router.urls
