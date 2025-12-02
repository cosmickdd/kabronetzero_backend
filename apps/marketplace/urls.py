"""
Marketplace app URLs
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.marketplace.views import ListingViewSet, OrderViewSet

router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listing')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = router.urls
