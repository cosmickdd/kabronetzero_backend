"""
Tokenization app URLs
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from tokenization.views import TokenizationJobViewSet

router = DefaultRouter()
router.register(r'jobs', TokenizationJobViewSet, basename='tokenization-job')

urlpatterns = router.urls
