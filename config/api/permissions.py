"""
DRF Permission classes for role-based access control
"""

from rest_framework import permissions
from accounts.models import UserRoleChoices, UserProfile


class IsAdminUser(permissions.BasePermission):
    """Allow access only to admin users"""
    
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        try:
            profile = UserProfile.objects.get(django_user_id=str(user.id))
            return profile.role == UserRoleChoices.ADMIN
        except UserProfile.DoesNotExist:
            return False


class IsValidator(permissions.BasePermission):
    """Allow access to validators and admins"""
    
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        try:
            profile = UserProfile.objects.get(django_user_id=str(user.id))
            return profile.role in [UserRoleChoices.VALIDATOR, UserRoleChoices.ADMIN]
        except UserProfile.DoesNotExist:
            return False


class IsRegulator(permissions.BasePermission):
    """Allow access to regulators and admins"""
    
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        try:
            profile = UserProfile.objects.get(django_user_id=str(user.id))
            return profile.role in [UserRoleChoices.REGULATOR, UserRoleChoices.ADMIN]
        except UserProfile.DoesNotExist:
            return False


class IsBuyer(permissions.BasePermission):
    """Allow access to buyers and admins"""
    
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        try:
            profile = UserProfile.objects.get(django_user_id=str(user.id))
            return profile.role in [UserRoleChoices.BUYER, UserRoleChoices.ADMIN]
        except UserProfile.DoesNotExist:
            return False


class IsOrgMember(permissions.BasePermission):
    """Allow access to organization members"""
    
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        try:
            profile = UserProfile.objects.get(django_user_id=str(user.id))
            return profile.role in [
                UserRoleChoices.ORG_OWNER,
                UserRoleChoices.ORG_MEMBER,
                UserRoleChoices.DEVELOPER,
                UserRoleChoices.ADMIN,
            ]
        except UserProfile.DoesNotExist:
            return False


class IsDeveloper(permissions.BasePermission):
    """Allow access to developers for API management"""
    
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        try:
            profile = UserProfile.objects.get(django_user_id=str(user.id))
            return profile.role in [UserRoleChoices.DEVELOPER, UserRoleChoices.ADMIN]
        except UserProfile.DoesNotExist:
            return False


class IsOrgOwner(permissions.BasePermission):
    """Allow access only to org owners"""
    
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        try:
            profile = UserProfile.objects.get(django_user_id=str(user.id))
            return profile.role in [UserRoleChoices.ORG_OWNER, UserRoleChoices.ADMIN]
        except UserProfile.DoesNotExist:
            return False


class IsOrgOwnerOrReadOnly(permissions.BasePermission):
    """Allow org owners full access, others read-only"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        try:
            profile = UserProfile.objects.get(django_user_id=str(user.id))
            return profile.role in [UserRoleChoices.ORG_OWNER, UserRoleChoices.ADMIN]
        except UserProfile.DoesNotExist:
            return False
