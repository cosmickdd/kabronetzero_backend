"""
URL routing for registration and authentication system
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
    path('register/org-owner/', RegisterOrgOwnerView.as_view(), name='register-org-owner'),
    path('register/buyer/', RegisterBuyerView.as_view(), name='register-buyer'),
    path('accept-invitation/', AcceptInvitationView.as_view(), name='accept-invitation'),
    path('register/validator/', RegisterValidatorView.as_view(), name='register-validator'),
    path('register/regulator/', RegisterRegulatorView.as_view(), name='register-regulator'),
    
    # Login
    path('login/', LoginView.as_view(), name='login'),
    
    # User profile
    path('me/', UserProfileView.as_view(), name='user-profile'),
    
    # Organization context
    path('organizations/', OrganizationListView.as_view(), name='list-organizations'),
    path('organizations/set-active/', OrganizationSetActiveView.as_view(), name='set-active-org'),
    
    # Member management
    path('organizations/<str:org_id>/members/invite/', OrganizationMemberInviteView.as_view(), name='invite-member'),
    path('organizations/<str:org_id>/members/', OrganizationMemberListView.as_view(), name='list-members'),
    path('organizations/<str:org_id>/members/remove/', OrganizationMemberRemoveView.as_view(), name='remove-member'),
    path('organizations/<str:org_id>/members/role/', OrganizationMemberRoleUpdateView.as_view(), name='update-member-role'),
]
