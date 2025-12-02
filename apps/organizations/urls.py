"""
Organizations app URLs
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from organizations.views import OrganizationViewSet, OrganizationMembershipViewSet

router = DefaultRouter()
router.register(r'', OrganizationViewSet, basename='organization')
router.register(r'memberships', OrganizationMembershipViewSet, basename='membership')

urlpatterns = router.urls
