"""
Regulator app URLs
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.regulator.views import RegulatorViewSet

router = DefaultRouter()
router.register(r'', RegulatorViewSet, basename='regulator')

urlpatterns = router.urls
