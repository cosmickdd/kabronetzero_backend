"""
Tokenization views
"""

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action


class TokenizationJobViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        return Response([])
    
    def create(self, request):
        return Response({'id': '1'}, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, pk=None):
        return Response({'id': pk})
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        return Response({'status': 'PENDING'})
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        return Response({'message': 'Tokenization job retried'})
