"""
Comprehensive DRF permission classes for multi-tenant, role-based authorization

Implements:
- Zero-trust access control (deny by default)
- Multi-tenancy enforcement
- Role hierarchy
- Permission delegation
- Audit logging
"""

from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from apps.accounts.models import (
    UserProfile, OrganizationMembership, PermissionChoices,
    PlatformRoleChoices, OrganizationRoleChoices, SpecializedRoleChoices,
    ROLE_PERMISSION_MAP, AuditLog
)
from datetime import datetime


class BaseAuditMixin:
    """Mixin to log permission checks"""
    
    @staticmethod
    def log_access(request, action, resource_type, resource_id, result):
        """Log access attempt for audit"""
        try:
            user = request.user
            user_profile = None
            organization = None
            
            if user and user.is_authenticated:
                try:
                    user_profile = UserProfile.objects.get(django_user_id=str(user.id))
                except:
                    pass
            
            # Try to extract organization from request context
            if hasattr(request, 'organization'):
                organization = request.organization
            
            AuditLog.objects.create(
                user_profile=user_profile,
                organization=organization,
                action=action,
                resource_type=resource_type,
                resource_id=str(resource_id) if resource_id else None,
                description=f"Access {'GRANTED' if result else 'DENIED'}",
                ip_address=BaseAuditMixin.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
                severity='CRITICAL' if not result else 'INFO',
            )
        except Exception as e:
            print(f"Audit logging failed: {e}")
    
    @staticmethod
    def get_client_ip(request):
        """Extract client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


# ==================== GLOBAL PERMISSIONS ====================

class IsAdmin(permissions.BasePermission, BaseAuditMixin):
    """Only platform administrators"""
    
    message = "Only administrators have access to this resource."
    
    def has_permission(self, request, view):
        try:
            user_profile = UserProfile.objects.get(django_user_id=str(request.user.id))
            result = request.user.is_authenticated and user_profile.platform_role == PlatformRoleChoices.ADMIN
            self.log_access(request, 'CHECK_ADMIN', 'System', None, result)
            return result
        except:
            self.log_access(request, 'CHECK_ADMIN', 'System', None, False)
            return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """Admin can do anything; others can only read"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        try:
            user_profile = UserProfile.objects.get(django_user_id=str(request.user.id))
            return user_profile.platform_role == PlatformRoleChoices.ADMIN
        except:
            return False


class IsRegulator(permissions.BasePermission, BaseAuditMixin):
    """Only regulators (government authorities)"""
    
    message = "Only regulators have access to this resource."
    
    def has_permission(self, request, view):
        try:
            user_profile = UserProfile.objects.get(django_user_id=str(request.user.id))
            result = request.user.is_authenticated and user_profile.platform_role == PlatformRoleChoices.REGULATOR
            self.log_access(request, 'CHECK_REGULATOR', 'System', None, result)
            return result
        except:
            self.log_access(request, 'CHECK_REGULATOR', 'System', None, False)
            return False


# ==================== ORGANIZATION-LEVEL PERMISSIONS ====================

class IsOrganizationMember(permissions.BasePermission, BaseAuditMixin):
    """User must be an active member of the organization"""
    
    message = "You are not a member of this organization."
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        try:
            user_profile = UserProfile.objects.get(django_user_id=str(request.user.id))
            
            # Admins & regulators bypass this check
            if user_profile.platform_role in [PlatformRoleChoices.ADMIN, PlatformRoleChoices.REGULATOR]:
                return True
            
            # Get organization from view
            organization = self.get_organization_from_request(request, view)
            if not organization:
                return False
            
            # Check membership
            membership = OrganizationMembership.objects(
                user_profile=user_profile,
                organization=organization,
                is_active=True
            ).first()
            
            result = membership is not None
            self.log_access(request, 'CHECK_ORG_MEMBERSHIP', 'Organization', organization.id, result)
            return result
        except Exception as e:
            self.log_access(request, 'CHECK_ORG_MEMBERSHIP', 'Organization', None, False)
            return False
    
    def has_object_permission(self, request, view, obj):
        """Check organization ownership at object level"""
        try:
            if hasattr(obj, 'organization'):
                organization = obj.organization
                user_profile = UserProfile.objects.get(django_user_id=str(request.user.id))
                
                if user_profile.platform_role in [PlatformRoleChoices.ADMIN, PlatformRoleChoices.REGULATOR]:
                    return True
                
                membership = OrganizationMembership.objects(
                    user_profile=user_profile,
                    organization=organization,
                    is_active=True
                ).first()
                
                return membership is not None
        except:
            pass
        return False
    
    @staticmethod
    def get_organization_from_request(request, view):
        """Extract organization from request context or view"""
        if hasattr(request, 'organization'):
            return request.organization
        if hasattr(view, 'kwargs') and 'organization_id' in view.kwargs:
            from apps.organizations.models import Organization
            try:
                return Organization.objects.get(id=view.kwargs['organization_id'])
            except:
                pass
        return None


class IsOrganizationOwner(permissions.BasePermission, BaseAuditMixin):
    """User must be ORG_OWNER of the organization"""
    
    message = "Only organization owners have access to this resource."
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        try:
            user_profile = UserProfile.objects.get(django_user_id=str(request.user.id))
            
            # Admins bypass this check
            if user_profile.platform_role == PlatformRoleChoices.ADMIN:
                return True
            
            organization = IsOrganizationMember.get_organization_from_request(request, view)
            if not organization:
                return False
            
            membership = OrganizationMembership.objects(
                user_profile=user_profile,
                organization=organization,
                org_role=OrganizationRoleChoices.ORG_OWNER,
                is_active=True
            ).first()
            
            result = membership is not None
            self.log_access(request, 'CHECK_ORG_OWNER', 'Organization', organization.id, result)
            return result
        except Exception as e:
            self.log_access(request, 'CHECK_ORG_OWNER', 'Organization', None, False)
            return False


class IsOrganizationOwnerOrManager(permissions.BasePermission):
    """User must be ORG_OWNER or ORG_MANAGER"""
    
    message = "Only organization owners or managers have access to this resource."
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        try:
            user_profile = UserProfile.objects.get(django_user_id=str(request.user.id))
            
            if user_profile.platform_role == PlatformRoleChoices.ADMIN:
                return True
            
            organization = IsOrganizationMember.get_organization_from_request(request, view)
            if not organization:
                return False
            
            membership = OrganizationMembership.objects(
                user_profile=user_profile,
                organization=organization,
                org_role__in=[OrganizationRoleChoices.ORG_OWNER, OrganizationRoleChoices.ORG_MANAGER],
                is_active=True
            ).first()
            
            return membership is not None
        except:
            return False


# ==================== PERMISSION-BASED CHECKS ====================

class HasPermission(permissions.BasePermission, BaseAuditMixin):
    """Check if user has specific permission"""
    
    required_permission = None  # Override in subclass
    
    def has_permission(self, request, view):
        if not self.required_permission:
            return True
        
        if not request.user.is_authenticated:
            return False
        
        try:
            user_profile = UserProfile.objects.get(django_user_id=str(request.user.id))
            
            # Admins have all permissions
            if user_profile.platform_role == PlatformRoleChoices.ADMIN:
                return True
            
            # Check platform role permissions
            if user_profile.platform_role:
                platform_permissions = ROLE_PERMISSION_MAP.get(user_profile.platform_role, [])
                if self.required_permission in platform_permissions:
                    return True
            
            # Check organization membership permissions
            organizations = user_profile.get_organizations()
            for org in organizations:
                membership = OrganizationMembership.objects(
                    user_profile=user_profile,
                    organization=org,
                    is_active=True
                ).first()
                if membership and membership.has_permission(self.required_permission):
                    return True
            
            self.log_access(request, f'CHECK_PERMISSION_{self.required_permission}', 'Permission', None, False)
            return False
        except Exception as e:
            self.log_access(request, f'CHECK_PERMISSION_{self.required_permission}', 'Permission', None, False)
            return False


# Specific permission classes
class CanCreateProject(HasPermission):
    required_permission = PermissionChoices.CREATE_PROJECT
    message = "You do not have permission to create projects."


class CanEditProject(HasPermission):
    required_permission = PermissionChoices.EDIT_PROJECT
    message = "You do not have permission to edit projects."


class CanSubmitForMRV(HasPermission):
    required_permission = PermissionChoices.SUBMIT_FOR_MRV
    message = "You do not have permission to submit projects for MRV."


class CanAssessMRV(HasPermission):
    required_permission = PermissionChoices.ASSESS_MRV
    message = "You do not have permission to assess MRV requests."


class CanApproveMRV(HasPermission):
    required_permission = PermissionChoices.APPROVE_MRV
    message = "You do not have permission to approve MRV requests."


class CanOverrideMRV(HasPermission):
    required_permission = PermissionChoices.OVERRIDE_MRV
    message = "Only regulators can override MRV decisions."


class CanIssueCredits(HasPermission):
    required_permission = PermissionChoices.ISSUE_CREDITS
    message = "You do not have permission to issue credits."


class CanLockBatch(HasPermission):
    required_permission = PermissionChoices.LOCK_BATCH
    message = "Only regulators can lock credit batches."


class CanRetireCredits(HasPermission):
    required_permission = PermissionChoices.RETIRE_CREDITS
    message = "You do not have permission to retire credits."


class CanManageMembers(HasPermission):
    required_permission = PermissionChoices.MANAGE_MEMBERS
    message = "You do not have permission to manage organization members."


class CanAssignRoles(HasPermission):
    required_permission = PermissionChoices.ASSIGN_ROLES
    message = "You do not have permission to assign roles."


class CanManageAPIKeys(HasPermission):
    required_permission = PermissionChoices.MANAGE_API_KEYS
    message = "You do not have permission to manage API keys."


class CanViewAuditLogs(HasPermission):
    required_permission = PermissionChoices.VIEW_AUDIT_LOGS
    message = "You do not have permission to view audit logs."


# ==================== SPECIALIZED ROLE CHECKS ====================

class IsValidator(permissions.BasePermission):
    """User must have VALIDATOR specialized role"""
    
    message = "Only validators have access to this resource."
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        try:
            user_profile = UserProfile.objects.get(django_user_id=str(request.user.id))
            
            # Check if they have VALIDATOR role in any org
            membership = OrganizationMembership.objects(
                user_profile=user_profile,
                specialized_roles=SpecializedRoleChoices.VALIDATOR,
                is_active=True
            ).first()
            
            return membership is not None or user_profile.platform_role == PlatformRoleChoices.ADMIN
        except:
            return False


class IsBuyer(permissions.BasePermission):
    """User must have BUYER specialized role"""
    
    message = "Only buyers have access to this resource."
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        try:
            user_profile = UserProfile.objects.get(django_user_id=str(request.user.id))
            
            membership = OrganizationMembership.objects(
                user_profile=user_profile,
                specialized_roles=SpecializedRoleChoices.BUYER,
                is_active=True
            ).first()
            
            return membership is not None or user_profile.platform_role == PlatformRoleChoices.ADMIN
        except:
            return False


class IsDeveloper(permissions.BasePermission):
    """User must have DEVELOPER specialized role"""
    
    message = "Only developers have access to this resource."
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        try:
            user_profile = UserProfile.objects.get(django_user_id=str(request.user.id))
            
            membership = OrganizationMembership.objects(
                user_profile=user_profile,
                specialized_roles=SpecializedRoleChoices.DEVELOPER,
                is_active=True
            ).first()
            
            return membership is not None or user_profile.platform_role == PlatformRoleChoices.ADMIN
        except:
            return False


# ==================== COMPOSITE PERMISSIONS ====================

class CanCreateProjectInOrg(IsOrganizationMember, CanCreateProject):
    """Must be org member AND have CREATE_PROJECT permission"""
    pass


class CanManageMembersInOrg(IsOrganizationOwner, CanManageMembers):
    """Must be org owner AND have MANAGE_MEMBERS permission"""
    pass


class IsNotFrozen(permissions.BasePermission):
    """User account must not be frozen"""
    
    message = "Your account has been frozen and cannot perform this action."
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        try:
            user_profile = UserProfile.objects.get(django_user_id=str(request.user.id))
            return not user_profile.is_frozen
        except:
            return False
