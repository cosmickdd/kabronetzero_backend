"""
Registry app URLs
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.registry.views import CreditBatchViewSet, CreditTransactionLogViewSet

router = DefaultRouter()
router.register(r'batches', CreditBatchViewSet, basename='credit-batch')
router.register(r'transactions', CreditTransactionLogViewSet, basename='transaction-log')

urlpatterns = router.urls
