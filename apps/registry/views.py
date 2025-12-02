"""
Registry views
"""

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action


class CreditBatchViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        return Response([])
    
    def retrieve(self, request, pk=None):
        return Response({'id': pk})
    
    @action(detail=True, methods=['get'])
    def credits(self, request, pk=None):
        return Response([])
    
    @action(detail=True, methods=['post'])
    def lock(self, request, pk=None):
        return Response({'message': 'Batch locked'})


class CreditTransactionLogViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        return Response([])
    
    def retrieve(self, request, pk=None):
        return Response({'id': pk})
