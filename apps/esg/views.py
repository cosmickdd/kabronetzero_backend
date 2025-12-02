"""
ESG views
"""

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action


class EmissionInventoryViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        return Response([])
    
    def create(self, request):
        return Response({'id': '1'}, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, pk=None):
        return Response({'id': pk})


class ESGReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        return Response([])
    
    def create(self, request):
        return Response({'id': '1'}, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, pk=None):
        return Response({'id': pk})
    
    @action(detail=False, methods=['post'])
    def generate_report(self, request):
        organization_id = request.data.get('organization_id')
        report_year = request.data.get('report_year')
        return Response({
            'message': f'ESG report generated for {report_year}',
            'organization_id': organization_id
        }, status=status.HTTP_201_CREATED)
