"""
URL routing for new registration and authentication system
"""

from django.urls import path
from apps.accounts.views import (
    RegisterOrgOwnerView, RegisterBuyerView, AcceptInvitationView,
    RegisterValidatorView, RegisterRegulatorView, LoginView,
    UserProfileView, OrganizationListView, OrganizationSetActiveView,
    OrganizationMemberInviteView, OrganizationMemberListView,
    OrganizationMemberRemoveView, OrganizationMemberRoleUpdateView
)

urlpatterns = [
    # Registration endpoints
    path('v1/auth/register/org-owner/', RegisterOrgOwnerView.as_view(), name='register-org-owner'),
    path('v1/auth/register/buyer/', RegisterBuyerView.as_view(), name='register-buyer'),
    path('v1/auth/accept-invitation/', AcceptInvitationView.as_view(), name='accept-invitation'),
    path('v1/auth/register/validator/', RegisterValidatorView.as_view(), name='register-validator'),
    path('v1/auth/register/regulator/', RegisterRegulatorView.as_view(), name='register-regulator'),
    
    # Login
    path('v1/auth/login/', LoginView.as_view(), name='login'),
    
    # User profile
    path('v1/auth/me/', UserProfileView.as_view(), name='user-profile'),
    
    # Organization context
    path('v1/auth/organizations/', OrganizationListView.as_view(), name='list-organizations'),
    path('v1/auth/organizations/set-active/', OrganizationSetActiveView.as_view(), name='set-active-org'),
    
    # Member management
    path('v1/organizations/<str:org_id>/members/invite/', OrganizationMemberInviteView.as_view(), name='invite-member'),
    path('v1/organizations/<str:org_id>/members/', OrganizationMemberListView.as_view(), name='list-members'),
    path('v1/organizations/<str:org_id>/members/remove/', OrganizationMemberRemoveView.as_view(), name='remove-member'),
    path('v1/organizations/<str:org_id>/members/role/', OrganizationMemberRoleUpdateView.as_view(), name='update-member-role'),
]
