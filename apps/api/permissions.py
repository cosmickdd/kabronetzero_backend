"""
API permissions module
"""

from rest_framework import permissions


class IsOrgOwner(permissions.BasePermission):
    """Permission to check if user is organization owner"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsAdminUser(permissions.BasePermission):
    """Permission to check if user is admin"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and getattr(request.user, 'is_staff', False)
