"""
ESG app URLs
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from esg.views import EmissionInventoryViewSet, ESGReportViewSet

router = DefaultRouter()
router.register(r'inventory', EmissionInventoryViewSet, basename='emission-inventory')
router.register(r'reports', ESGReportViewSet, basename='esg-report')

urlpatterns = router.urls
