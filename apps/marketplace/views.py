"""
Marketplace views
"""

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action


class ListingViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        return Response([])
    
    def create(self, request):
        return Response({'id': '1'}, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, pk=None):
        return Response({'id': pk})


class OrderViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        return Response([])
    
    def create(self, request):
        return Response({'id': '1'}, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, pk=None):
        return Response({'id': pk})
    
    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        return Response({'message': 'Payment confirmed'})
