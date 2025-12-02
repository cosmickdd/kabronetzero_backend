"""
Retirement app URLs
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.retirement.views import RetirementRecordViewSet

router = DefaultRouter()
router.register(r'records', RetirementRecordViewSet, basename='retirement-record')

urlpatterns = router.urls
