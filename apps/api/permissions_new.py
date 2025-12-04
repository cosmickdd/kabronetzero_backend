"""
Permission classes for multi-tenant organization-based access control
Implements header-based org scoping with role-based authorization
"""

from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from apps.organizations.models import OrganizationMembership
from apps.accounts.models import PlatformRoleChoices


class IsOrgMemberWithRole(BasePermission):
    """
    Base permission class for organization-scoped access
    Checks X-Org-Id header/query param for org scoping
    Verifies membership exists and user has allowed role
    """
    allowed_roles = []  # Override in subclass
    check_global_role = False  # If True, also check global_role field
    allowed_global_roles = []
    
    def get_org_id_from_request(self, request):
        """Extract org_id from X-Org-Id header or query param"""
        org_id = request.headers.get('X-Org-Id')
        if not org_id:
            org_id = request.query_params.get('org_id')
        if not org_id:
            org_id = request.data.get('org_id') if hasattr(request, 'data') else None
        return org_id
    
    def has_permission(self, request, view):
        """Check if user has permission based on org membership and role"""
        user = request.user
        
        # Anonymous users have no access
        if not user or not user.is_authenticated:
            return False
        
        # Check global role first (for admins/validators/regulators)
        if self.check_global_role and user.global_role in self.allowed_global_roles:
            return True
        
        # Get organization ID from request
        org_id = self.get_org_id_from_request(request)
        
        if not org_id:
            return False
        
        # Check membership and role
        membership = OrganizationMembership.objects.filter(
            user=user,
            organization_id=org_id,
            is_active=True
        ).first()
        
        if not membership:
            return False
        
        # Check if user's role is in allowed_roles
        if not self.allowed_roles:  # If no specific roles required
            return True
        
        if membership.role_in_org not in self.allowed_roles:
            return False
        
        # Attach org context to request for later use
        request.org_id = str(org_id)
        request.membership = membership
        
        return True


# ==================== BASIC ORG ROLES ====================

class IsOrgOwner(IsOrgMemberWithRole):
    """Only ORG_OWNER can access"""
    allowed_roles = ['ORG_OWNER']


class IsOrgOwnerOrManager(IsOrgMemberWithRole):
    """ORG_OWNER or ORG_MANAGER can access"""
    allowed_roles = ['ORG_OWNER', 'ORG_MANAGER']


class IsOrgMember(IsOrgMemberWithRole):
    """Any active member can access"""
    allowed_roles = ['ORG_OWNER', 'ORG_MANAGER', 'ORG_MEMBER', 'DEVELOPER', 'BUYER']


# ==================== SPECIALIZED ROLES ====================

class IsBuyer(IsOrgMemberWithRole):
    """Only BUYER role can access"""
    allowed_roles = ['BUYER']


class IsDeveloper(IsOrgMemberWithRole):
    """Only DEVELOPER role can access"""
    allowed_roles = ['DEVELOPER']


class IsDeveloperOrMember(IsOrgMemberWithRole):
    """DEVELOPER or ORG_MEMBER can access"""
    allowed_roles = ['DEVELOPER', 'ORG_MEMBER']


# ==================== PLATFORM LEVEL ====================

class IsRegulatorOrAdmin(BasePermission):
    """
    Platform-level permission
    User must have REGULATOR or ADMIN global_role
    """
    
    def has_permission(self, request, view):
        user = request.user
        
        if not user or not user.is_authenticated:
            return False
        
        if user.global_role not in [PlatformRoleChoices.ADMIN, PlatformRoleChoices.REGULATOR]:
            return False
        
        return True


class IsValidator(BasePermission):
    """
    VALIDATOR role access
    Can be either global VALIDATOR or assigned validator role in org
    """
    
    def has_permission(self, request, view):
        user = request.user
        
        if not user or not user.is_authenticated:
            return False
        
        # Global validator
        if user.global_role == PlatformRoleChoices.VALIDATOR:
            return True
        
        # Check if has validator org membership
        org_id = self.get_org_id_from_request(request)
        if org_id:
            membership = OrganizationMembership.objects.filter(
                user=user,
                organization_id=org_id,
                role_in_org='VALIDATOR'  # If role exists
            ).exists()
            if membership:
                return True
        
        return False
    
    def get_org_id_from_request(self, request):
        org_id = request.headers.get('X-Org-Id')
        if not org_id:
            org_id = request.query_params.get('org_id')
        return org_id


class IsAdmin(BasePermission):
    """Only ADMIN role can access"""
    
    def has_permission(self, request, view):
        user = request.user
        
        if not user or not user.is_authenticated:
            return False
        
        return user.global_role == PlatformRoleChoices.ADMIN


class IsSuperUserOrAdmin(BasePermission):
    """Superuser or ADMIN role"""
    
    def has_permission(self, request, view):
        user = request.user
        
        if not user or not user.is_authenticated:
            return False
        
        return user.is_superuser or user.global_role == PlatformRoleChoices.ADMIN


# ==================== OWNERSHIP & OBJECT LEVEL ====================

class IsOrgOwnerOfObject(IsOrgMemberWithRole):
    """
    User must be ORG_OWNER of the organization that owns this object
    Assumes view has get_object() method
    """
    allowed_roles = ['ORG_OWNER']
    
    def has_object_permission(self, request, view, obj):
        """Check object-level permission"""
        user = request.user
        
        if not user or not user.is_authenticated:
            return False
        
        # Get org_id from object
        org_id = getattr(obj, 'organization_id', None)
        if not org_id:
            org_id = getattr(obj, 'organization', None)
            if org_id:
                org_id = org_id.id
        
        if not org_id:
            return False
        
        # Check membership
        membership = OrganizationMembership.objects.filter(
            user=user,
            organization_id=org_id,
            role_in_org='ORG_OWNER',
            is_active=True
        ).exists()
        
        return membership


class IsOrgMemberOfObject(BasePermission):
    """User must be member of org that owns object"""
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        if not user or not user.is_authenticated:
            return False
        
        org_id = getattr(obj, 'organization_id', None)
        if not org_id:
            org_id = getattr(obj, 'organization', None)
            if org_id:
                org_id = org_id.id
        
        if not org_id:
            return False
        
        membership = OrganizationMembership.objects.filter(
            user=user,
            organization_id=org_id,
            is_active=True
        ).exists()
        
        return membership


class IsObjectOwner(BasePermission):
    """User must be the creator/owner of the object"""
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        if not user or not user.is_authenticated:
            return False
        
        # Check common ownership fields
        owner_field = getattr(obj, 'created_by', None) or getattr(obj, 'owner', None) or getattr(obj, 'user', None)
        
        if owner_field:
            return owner_field.id == user.id
        
        return False


# ==================== COMPOSITE PERMISSIONS ====================

class IsOrgOwnerOrObjectOwner(BasePermission):
    """ORG_OWNER of org OR creator of object"""
    
    def has_permission(self, request, view):
        # First check org ownership
        org_id = self.get_org_id_from_request(request)
        if org_id:
            user = request.user
            if user and user.is_authenticated:
                membership = OrganizationMembership.objects.filter(
                    user=user,
                    organization_id=org_id,
                    role_in_org='ORG_OWNER',
                    is_active=True
                ).exists()
                if membership:
                    return True
        
        return True  # Allow object-level check
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        if not user or not user.is_authenticated:
            return False
        
        # Check org owner
        org_id = getattr(obj, 'organization_id', None)
        if not org_id:
            org_id = getattr(obj, 'organization', None)
            if org_id:
                org_id = org_id.id
        
        if org_id:
            is_org_owner = OrganizationMembership.objects.filter(
                user=user,
                organization_id=org_id,
                role_in_org='ORG_OWNER',
                is_active=True
            ).exists()
            if is_org_owner:
                return True
        
        # Check object owner
        owner_field = getattr(obj, 'created_by', None) or getattr(obj, 'owner', None) or getattr(obj, 'user', None)
        if owner_field and owner_field.id == user.id:
            return True
        
        return False
    
    def get_org_id_from_request(self, request):
        org_id = request.headers.get('X-Org-Id')
        if not org_id:
            org_id = request.query_params.get('org_id')
        return org_id


# ==================== CUSTOM LOGIC ====================

class CanModifyOrganization(BasePermission):
    """
    Can modify organization settings
    - ADMIN can modify any org
    - ORG_OWNER can modify own org
    """
    
    def has_permission(self, request, view):
        user = request.user
        
        if not user or not user.is_authenticated:
            return False
        
        # ADMIN can do anything
        if user.global_role == PlatformRoleChoices.ADMIN:
            return True
        
        # Get org_id
        org_id = self.get_org_id_from_request(request)
        if not org_id:
            return False
        
        # Must be ORG_OWNER
        membership = OrganizationMembership.objects.filter(
            user=user,
            organization_id=org_id,
            role_in_org='ORG_OWNER',
            is_active=True
        ).exists()
        
        return membership
    
    def get_org_id_from_request(self, request):
        org_id = request.headers.get('X-Org-Id')
        if not org_id:
            org_id = request.query_params.get('org_id')
        if not org_id:
            org_id = request.data.get('org_id') if hasattr(request, 'data') else None
        return org_id


class CanAccessProjectAsMember(IsOrgMemberWithRole):
    """
    Can access project if member of project org
    Must be DEVELOPER, MANAGER, or OWNER
    """
    allowed_roles = ['DEVELOPER', 'ORG_MANAGER', 'ORG_OWNER']
    allowed_global_roles = [PlatformRoleChoices.ADMIN, PlatformRoleChoices.REGULATOR]
    check_global_role = True


class CanValidateProject(BasePermission):
    """
    Can validate project
    - VALIDATOR role at platform or org level
    - REGULATOR or ADMIN at platform level
    """
    
    def has_permission(self, request, view):
        user = request.user
        
        if not user or not user.is_authenticated:
            return False
        
        # Platform-level validator/regulator/admin
        if user.global_role in [PlatformRoleChoices.VALIDATOR, PlatformRoleChoices.REGULATOR, PlatformRoleChoices.ADMIN]:
            return True
        
        # Org-level validator
        org_id = self.get_org_id_from_request(request)
        if org_id:
            # Could check for org-level validator membership if role exists
            pass
        
        return False
    
    def get_org_id_from_request(self, request):
        org_id = request.headers.get('X-Org-Id')
        if not org_id:
            org_id = request.query_params.get('org_id')
        return org_id
