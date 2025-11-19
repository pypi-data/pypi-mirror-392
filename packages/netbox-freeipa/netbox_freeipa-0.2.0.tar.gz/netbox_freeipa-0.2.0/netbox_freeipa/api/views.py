"""REST API views for NetBox FreeIPA plugin."""

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from netbox.api.viewsets import NetBoxModelViewSet

from ..models import FreeIPAHost, FreeIPADNSZone, FreeIPADNSRecord
from ..freeipa_client import FreeIPAClient
from .serializers import (
    FreeIPAHostSerializer,
    FreeIPADNSZoneSerializer,
    FreeIPADNSRecordSerializer,
)


class FreeIPAHostViewSet(NetBoxModelViewSet):
    """ViewSet for FreeIPAHost model."""
    
    queryset = FreeIPAHost.objects.prefetch_related('dns_records')
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


class FreeIPADNSZoneViewSet(NetBoxModelViewSet):
    """ViewSet for FreeIPADNSZone model."""
    
    queryset = FreeIPADNSZone.objects.prefetch_related('dns_records')
    serializer_class = FreeIPADNSZoneSerializer
    
    @action(detail=False, methods=['post'])
    def sync(self, request):
        """
        Trigger DNS zones synchronization with FreeIPA server.
        
        POST /api/plugins/freeipa/dns-zones/sync/
        """
        try:
            client = FreeIPAClient()
            stats = client.sync_dns_zones()
            
            return Response({
                'success': True,
                'message': 'DNS zones synchronization completed successfully',
                'statistics': stats
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Synchronization failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FreeIPADNSRecordViewSet(NetBoxModelViewSet):
    """ViewSet for FreeIPADNSRecord model."""
    
    queryset = FreeIPADNSRecord.objects.select_related('dns_zone', 'host')
    serializer_class = FreeIPADNSRecordSerializer
    filterset_fields = ['dns_zone', 'record_name', 'record_type', 'host']
    
    @action(detail=False, methods=['post'])
    def sync(self, request):
        """
        Trigger DNS records synchronization with FreeIPA server.
        
        POST /api/plugins/freeipa/dns-records/sync/
        """
        try:
            client = FreeIPAClient()
            stats = client.sync_dns_records()
            
            return Response({
                'success': True,
                'message': 'DNS records synchronization completed successfully',
                'statistics': stats
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Synchronization failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FreeIPASyncViewSet(NetBoxModelViewSet):
    """ViewSet for synchronizing all FreeIPA data."""
    
    queryset = FreeIPAHost.objects.none()  # No model backing
    serializer_class = FreeIPAHostSerializer  # Placeholder
    
    @action(detail=False, methods=['post'], url_path='all')
    def sync_all(self, request):
        """
        Trigger full synchronization of all FreeIPA data.
        
        POST /api/plugins/freeipa/sync/all/
        """
        try:
            client = FreeIPAClient()
            results = client.sync_all()
            
            return Response({
                'success': True,
                'message': 'Full synchronization completed',
                'results': results
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Synchronization failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
