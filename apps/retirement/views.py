"""
Retirement views
"""

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action


class RetirementRecordViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        return Response([])
    
    def create(self, request):
        return Response({'id': '1'}, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, pk=None):
        return Response({'id': pk})
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def public_certificate(self, request):
        reference_id = request.query_params.get('reference_id')
        return Response({
            'reference_id': reference_id,
            'organization': 'Example Org',
            'quantity': 100,
            'retirement_date': '2024-01-01'
        })
