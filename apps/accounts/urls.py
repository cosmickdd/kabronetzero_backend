"""
Accounts app URLs
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.accounts.views import (
    RegisterViewSet, AuthViewSet, ProfileViewSet,
    OrganizationManagementViewSet, AdminViewSet
)

router = DefaultRouter()
router.register(r'register', RegisterViewSet, basename='register')
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'organizations', OrganizationManagementViewSet, basename='org-management')
router.register(r'admin', AdminViewSet, basename='admin')

urlpatterns = router.urls
