"""
URL routing for new registration and authentication system
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.accounts.views_new import (
    RegisterOrgOwnerView, RegisterBuyerView, AcceptInvitationView,
    RegisterValidatorView, RegisterRegulatorView, LoginView,
    UserProfileView, OrganizationContextView, OrganizationMemberView
)

# Create router for viewsets
router = DefaultRouter()

# Registration routes (using create action)
router.register(r'auth/register/org-owner', RegisterOrgOwnerView, basename='register-org-owner')
router.register(r'auth/register/buyer', RegisterBuyerView, basename='register-buyer')
router.register(r'auth/accept-invitation', AcceptInvitationView, basename='accept-invitation')
router.register(r'auth/register/validator', RegisterValidatorView, basename='register-validator')
router.register(r'auth/register/regulator', RegisterRegulatorView, basename='register-regulator')
router.register(r'auth/login', LoginView, basename='login')
router.register(r'auth/me', UserProfileView, basename='user-profile')
router.register(r'auth/organizations', OrganizationContextView, basename='org-context')
router.register(r'organizations/members', OrganizationMemberView, basename='org-members')

urlpatterns = [
    path('v1/', include(router.urls)),
]
