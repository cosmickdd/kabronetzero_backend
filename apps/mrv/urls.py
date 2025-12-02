"""
MRV app URLs
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from mrv.views import MRVRequestViewSet, MRVAssessmentViewSet

router = DefaultRouter()
router.register(r'requests', MRVRequestViewSet, basename='mrv-request')
router.register(r'assessments', MRVAssessmentViewSet, basename='mrv-assessment')

urlpatterns = router.urls
