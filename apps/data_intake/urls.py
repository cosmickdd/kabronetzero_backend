"""
Data Intake app URLs
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.data_intake.views import DataSourceViewSet, DataPointViewSet

router = DefaultRouter()
router.register(r'sources', DataSourceViewSet, basename='data-source')
router.register(r'points', DataPointViewSet, basename='data-point')

urlpatterns = router.urls
