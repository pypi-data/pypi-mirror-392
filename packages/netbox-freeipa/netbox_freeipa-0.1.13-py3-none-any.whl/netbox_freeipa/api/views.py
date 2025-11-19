"""REST API views for NetBox FreeIPA plugin."""

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from netbox.api.viewsets import NetBoxModelViewSet

from ..models import FreeIPAHost
from ..freeipa_client import FreeIPAClient
from .serializers import FreeIPAHostSerializer


class FreeIPAHostViewSet(NetBoxModelViewSet):
    """ViewSet for FreeIPAHost model."""
    
    queryset = FreeIPAHost.objects.all()
    serializer_class = FreeIPAHostSerializer
    
    @action(detail=False, methods=['post'])
    def sync(self, request):
        """
        Trigger synchronization with FreeIPA server.
        
        POST /api/plugins/freeipa/hosts/sync/
        """
        try:
            client = FreeIPAClient()
            stats = client.sync_hosts()
            
            return Response({
                'success': True,
                'message': 'Synchronization completed successfully',
                'statistics': stats
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Synchronization failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def refresh(self, request, pk=None):
        """
        Refresh a specific host from FreeIPA.
        
        GET /api/plugins/freeipa/hosts/{id}/refresh/
        """
        host = self.get_object()
        
        try:
            client = FreeIPAClient()
            host_data = client.get_host_details(host.fqdn)
            
            if host_data:
                parsed_data = client.parse_host_data(host_data)
                
                # Update host with fresh data
                for key, value in parsed_data.items():
                    setattr(host, key, value)
                host.save()
                
                serializer = self.get_serializer(host)
                return Response({
                    'success': True,
                    'message': f'Host {host.fqdn} refreshed successfully',
                    'host': serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': f'Host {host.fqdn} not found in FreeIPA'
                }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Failed to refresh host: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            client.disconnect()
