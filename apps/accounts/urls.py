"""
Accounts app URLs
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.accounts.views import UserProfileViewSet, RegisterViewSet

router = DefaultRouter()
router.register(r'register', RegisterViewSet, basename='register')
router.register(r'me', UserProfileViewSet, basename='user-me')

urlpatterns = router.urls
