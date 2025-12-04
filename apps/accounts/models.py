"""
Accounts app models - Multi-tenant, hierarchical authorization system
Global CustomUser with organization-specific roles
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from mongoengine import (
    Document, StringField, EmailField, BooleanField, DateTimeField,
    ReferenceField, ListField, DictField, IntField, DecimalField,
    EmbeddedDocument, EmbeddedDocumentField, ObjectIdField
)
from datetime import datetime, timedelta
import uuid
import hmac
import hashlib


# ==================== ROLE & PERMISSION CONSTANTS ====================

class PlatformRoleChoices:
    """Platform-wide global roles"""
    ADMIN = 'ADMIN'
    REGULATOR = 'REGULATOR'
    VALIDATOR = 'VALIDATOR'  # Global validator (special)
    NORMAL_USER = 'NORMAL_USER'  # Default for all users
    
    CHOICES = [
        (ADMIN, 'Administrator'),
        (REGULATOR, 'Regulator'),
        (VALIDATOR, 'Global MRV Validator'),
        (NORMAL_USER, 'Normal User'),
    ]


class OrganizationRoleChoices:
    """Organization-level roles (within an organization)"""
    ORG_OWNER = 'ORG_OWNER'
    ORG_MANAGER = 'ORG_MANAGER'
    ORG_MEMBER = 'ORG_MEMBER'
    DEVELOPER = 'DEVELOPER'  # Can be org role too
    BUYER = 'BUYER'  # Can be org role too
    
    CHOICES = [
        (ORG_OWNER, 'Organization Owner'),
        (ORG_MANAGER, 'Organization Manager'),
        (ORG_MEMBER, 'Organization Member'),
        (DEVELOPER, 'Developer'),
        (BUYER, 'Buyer'),
    ]


class SpecializedRoleChoices:
    """Specialized roles (cross-cutting)"""
    VALIDATOR = 'VALIDATOR'
    BUYER = 'BUYER'
    DEVELOPER = 'DEVELOPER'
    
    CHOICES = [
        (VALIDATOR, 'MRV Validator'),
        (BUYER, 'Carbon Buyer'),
        (DEVELOPER, 'Developer'),
    ]


class PermissionChoices:
    """Granular permission constants"""
    
    # Project permissions
    CREATE_PROJECT = 'CREATE_PROJECT'
    EDIT_PROJECT = 'EDIT_PROJECT'
    DELETE_PROJECT = 'DELETE_PROJECT'
    VIEW_PROJECT = 'VIEW_PROJECT'
    SUBMIT_FOR_MRV = 'SUBMIT_FOR_MRV'
    
    # Data intake permissions
    UPLOAD_DATA = 'UPLOAD_DATA'
    VIEW_DATA = 'VIEW_DATA'
    DELETE_DATA = 'DELETE_DATA'
    
    # MRV permissions
    ASSESS_MRV = 'ASSESS_MRV'
    VIEW_MRV = 'VIEW_MRV'
    APPROVE_MRV = 'APPROVE_MRV'  # Regulator only
    OVERRIDE_MRV = 'OVERRIDE_MRV'  # Regulator only
    
    # Registry permissions
    ISSUE_CREDITS = 'ISSUE_CREDITS'
    VIEW_REGISTRY = 'VIEW_REGISTRY'
    LOCK_BATCH = 'LOCK_BATCH'  # Regulator only
    
    # Marketplace permissions
    LIST_CREDITS = 'LIST_CREDITS'
    CREATE_ORDER = 'CREATE_ORDER'
    VIEW_LISTINGS = 'VIEW_LISTINGS'
    
    # Retirement permissions
    RETIRE_CREDITS = 'RETIRE_CREDITS'
    VIEW_RETIREMENT = 'VIEW_RETIREMENT'
    
    # ESG permissions
    CREATE_ESG_REPORT = 'CREATE_ESG_REPORT'
    VIEW_ESG_REPORT = 'VIEW_ESG_REPORT'
    
    # Organization permissions
    MANAGE_MEMBERS = 'MANAGE_MEMBERS'
    INVITE_USERS = 'INVITE_USERS'
    ASSIGN_ROLES = 'ASSIGN_ROLES'
    
    # API/Integration permissions
    MANAGE_API_KEYS = 'MANAGE_API_KEYS'
    MANAGE_WEBHOOKS = 'MANAGE_WEBHOOKS'
    
    # Admin permissions
    SYSTEM_ADMIN = 'SYSTEM_ADMIN'
    VIEW_AUDIT_LOGS = 'VIEW_AUDIT_LOGS'
    MANAGE_ROLES = 'MANAGE_ROLES'
    FREEZE_ACCOUNT = 'FREEZE_ACCOUNT'
    
    ALL_PERMISSIONS = [
        CREATE_PROJECT, EDIT_PROJECT, DELETE_PROJECT, VIEW_PROJECT, SUBMIT_FOR_MRV,
        UPLOAD_DATA, VIEW_DATA, DELETE_DATA,
        ASSESS_MRV, VIEW_MRV, APPROVE_MRV, OVERRIDE_MRV,
        ISSUE_CREDITS, VIEW_REGISTRY, LOCK_BATCH,
        LIST_CREDITS, CREATE_ORDER, VIEW_LISTINGS,
        RETIRE_CREDITS, VIEW_RETIREMENT,
        CREATE_ESG_REPORT, VIEW_ESG_REPORT,
        MANAGE_MEMBERS, INVITE_USERS, ASSIGN_ROLES,
        MANAGE_API_KEYS, MANAGE_WEBHOOKS,
        SYSTEM_ADMIN, VIEW_AUDIT_LOGS, MANAGE_ROLES, FREEZE_ACCOUNT,
    ]


# ==================== ROLE-PERMISSION MAPPING ====================

ROLE_PERMISSION_MAP = {
    # ADMIN - Full system access
    'ADMIN': PermissionChoices.ALL_PERMISSIONS,
    
    # REGULATOR - Read all, override MRV/Registry
    'REGULATOR': [
        PermissionChoices.VIEW_PROJECT,
        PermissionChoices.VIEW_DATA,
        PermissionChoices.VIEW_MRV,
        PermissionChoices.APPROVE_MRV,
        PermissionChoices.OVERRIDE_MRV,
        PermissionChoices.VIEW_REGISTRY,
        PermissionChoices.LOCK_BATCH,
        PermissionChoices.VIEW_LISTINGS,
        PermissionChoices.VIEW_RETIREMENT,
        PermissionChoices.VIEW_ESG_REPORT,
        PermissionChoices.VIEW_AUDIT_LOGS,
    ],
    
    # ORG_OWNER - Full org control
    'ORG_OWNER': [
        PermissionChoices.CREATE_PROJECT,
        PermissionChoices.EDIT_PROJECT,
        PermissionChoices.DELETE_PROJECT,
        PermissionChoices.VIEW_PROJECT,
        PermissionChoices.SUBMIT_FOR_MRV,
        PermissionChoices.UPLOAD_DATA,
        PermissionChoices.VIEW_DATA,
        PermissionChoices.DELETE_DATA,
        PermissionChoices.VIEW_MRV,
        PermissionChoices.ISSUE_CREDITS,
        PermissionChoices.VIEW_REGISTRY,
        PermissionChoices.LIST_CREDITS,
        PermissionChoices.CREATE_ORDER,
        PermissionChoices.VIEW_LISTINGS,
        PermissionChoices.RETIRE_CREDITS,
        PermissionChoices.VIEW_RETIREMENT,
        PermissionChoices.CREATE_ESG_REPORT,
        PermissionChoices.VIEW_ESG_REPORT,
        PermissionChoices.MANAGE_MEMBERS,
        PermissionChoices.INVITE_USERS,
        PermissionChoices.ASSIGN_ROLES,
        PermissionChoices.MANAGE_API_KEYS,
        PermissionChoices.MANAGE_WEBHOOKS,
        PermissionChoices.VIEW_AUDIT_LOGS,
    ],
    
    # ORG_MANAGER - Operational control
    'ORG_MANAGER': [
        PermissionChoices.CREATE_PROJECT,
        PermissionChoices.EDIT_PROJECT,
        PermissionChoices.VIEW_PROJECT,
        PermissionChoices.SUBMIT_FOR_MRV,
        PermissionChoices.UPLOAD_DATA,
        PermissionChoices.VIEW_DATA,
        PermissionChoices.VIEW_MRV,
        PermissionChoices.ISSUE_CREDITS,
        PermissionChoices.VIEW_REGISTRY,
        PermissionChoices.LIST_CREDITS,
        PermissionChoices.CREATE_ORDER,
        PermissionChoices.VIEW_LISTINGS,
        PermissionChoices.RETIRE_CREDITS,
        PermissionChoices.VIEW_RETIREMENT,
        PermissionChoices.CREATE_ESG_REPORT,
        PermissionChoices.VIEW_ESG_REPORT,
        PermissionChoices.VIEW_AUDIT_LOGS,
    ],
    
    # ORG_MEMBER - Collaborator
    'ORG_MEMBER': [
        PermissionChoices.VIEW_PROJECT,
        PermissionChoices.UPLOAD_DATA,
        PermissionChoices.VIEW_DATA,
        PermissionChoices.VIEW_MRV,
        PermissionChoices.VIEW_REGISTRY,
        PermissionChoices.VIEW_LISTINGS,
        PermissionChoices.VIEW_RETIREMENT,
        PermissionChoices.VIEW_ESG_REPORT,
    ],
    
    # VALIDATOR - MRV only
    'VALIDATOR': [
        PermissionChoices.VIEW_MRV,
        PermissionChoices.ASSESS_MRV,
        PermissionChoices.VIEW_PROJECT,  # Context only
    ],
    
    # BUYER - Marketplace & Retirement
    'BUYER': [
        PermissionChoices.VIEW_LISTINGS,
        PermissionChoices.CREATE_ORDER,
        PermissionChoices.RETIRE_CREDITS,
        PermissionChoices.VIEW_RETIREMENT,
    ],
    
    # DEVELOPER - API/Webhooks
    'DEVELOPER': [
        PermissionChoices.VIEW_PROJECT,
        PermissionChoices.VIEW_DATA,
        PermissionChoices.VIEW_REGISTRY,
        PermissionChoices.MANAGE_API_KEYS,
        PermissionChoices.MANAGE_WEBHOOKS,
    ],
}


# ==================== CUSTOM USER MODEL ====================

class CustomUserManager(BaseUserManager):
    """Manager for CustomUser model"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        extra_fields.setdefault('global_role', PlatformRoleChoices.NORMAL_USER)
        extra_fields.setdefault('is_active', True)
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password) if password else None
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('global_role', PlatformRoleChoices.ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('global_role') != PlatformRoleChoices.ADMIN:
            raise ValueError('Superuser must have ADMIN role')
        
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Global CustomUser model - all users share one table
    Platform roles (ADMIN, REGULATOR, VALIDATOR, NORMAL_USER) are global
    Organization-specific roles live in OrganizationMembership
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    
    # Global platform role
    global_role = models.CharField(
        max_length=32,
        choices=PlatformRoleChoices.CHOICES,
        default=PlatformRoleChoices.NORMAL_USER
    )
    
    # Account status
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Can access admin site
    is_superuser = models.BooleanField(default=False)  # Full admin
    
    # Freeze capability
    is_frozen = models.BooleanField(default=False)
    freeze_reason = models.TextField(blank=True)
    frozen_at = models.DateTimeField(null=True, blank=True)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    
    class Meta:
        db_table = 'auth_customuser'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['global_role']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.email} ({self.global_role})"
    
    def get_active_organization(self):
        """Get user's active organization from session or first membership"""
        # TODO: Implement active_org_id from session/JWT
        from apps.organizations.models import OrganizationMembership
        membership = OrganizationMembership.objects(
            user=self,
            is_active=True
        ).order_by('-created_at').first()
        return membership.organization if membership else None
    
    def get_memberships(self):
        """Get all active organization memberships"""
        from apps.organizations.models import OrganizationMembership
        return OrganizationMembership.objects(user=self, is_active=True)


# ==================== MODELS ====================

class UserProfile(Document):
    """
    Enhanced user profile with multi-tenant, hierarchical roles
    """
    
    meta = {
        'collection': 'user_profiles',
        'indexes': [
            'django_user_id',
            'email',
            'platform_role',
            'is_active',
            'created_at',
        ],
    }
    
    # Link to Django User
    django_user_id = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    first_name = StringField(max_length=100)
    last_name = StringField(max_length=100)
    phone_number = StringField()
    
    # ==================== ROLES ====================
    
    # Platform-level role (ADMIN or REGULATOR)
    platform_role = StringField(
        choices=PlatformRoleChoices.CHOICES,
        default=None
    )
    
    # Profile metadata
    profile_picture_url = StringField()
    bio = StringField()
    
    # Status
    is_active = BooleanField(default=True)
    is_verified = BooleanField(default=False)
    is_frozen = BooleanField(default=False)  # Admin can freeze accounts
    freeze_reason = StringField()
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    last_login = DateTimeField()
    
    def has_permission(self, permission, organization=None):
        """Check if user has a specific permission"""
        if self.is_frozen:
            return False
        
        if self.platform_role == PlatformRoleChoices.ADMIN:
            return True  # Admins have all permissions
        
        if self.platform_role == PlatformRoleChoices.REGULATOR:
            return permission in ROLE_PERMISSION_MAP.get('REGULATOR', [])
        
        if organization:
            membership = OrganizationMembership.objects(
                user_profile=self, organization=organization
            ).first()
            if membership:
                return permission in membership.get_permissions()
        
        return False
    
    def get_organizations(self):
        """Get all organizations this user belongs to"""
        memberships = OrganizationMembership.objects(user_profile=self, is_active=True)
        return [m.organization for m in memberships]
    
    def __str__(self):
        role = self.platform_role or "User"
        return f"{self.email} ({role})"


class OrganizationMembership(Document):
    """
    Organization membership with role inheritance and delegation
    """
    
    meta = {
        'collection': 'organization_memberships',
        'indexes': [
            'organization',
            'user_profile',
            'org_role',
            'is_active',
            'created_at',
        ],
    }
    
    organization = ReferenceField('apps.organizations.Organization', required=True)
    user_profile = ReferenceField(UserProfile, required=True)
    
    # Role within this organization
    org_role = StringField(
        choices=OrganizationRoleChoices.CHOICES,
        required=True,
        default=OrganizationRoleChoices.ORG_MEMBER
    )
    
    # Additional specialized roles (non-mutually exclusive)
    specialized_roles = ListField(StringField(choices=SpecializedRoleChoices.CHOICES))
    
    # ==================== DELEGATION ====================
    
    delegated_permissions = ListField(StringField())  # Specific permissions granted
    delegated_by = ReferenceField(UserProfile)  # Who delegated
    delegation_start = DateTimeField()
    delegation_end = DateTimeField()  # Time-bound delegation
    delegation_reason = StringField()
    
    # ==================== PERMISSIONS ====================
    
    # Permission flags for data-level access
    can_create_projects = BooleanField(default=False)
    can_edit_projects = BooleanField(default=False)
    can_submit_data = BooleanField(default=False)
    can_manage_members = BooleanField(default=False)
    can_view_reports = BooleanField(default=True)
    can_issue_credits = BooleanField(default=False)
    can_list_credits = BooleanField(default=False)
    
    # Status
    is_active = BooleanField(default=True)
    invited_by = ReferenceField(UserProfile)
    accepted_at = DateTimeField()
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def get_permissions(self):
        """Get all permissions for this membership"""
        permissions = set(ROLE_PERMISSION_MAP.get(self.org_role, []))
        
        # Add specialized role permissions
        for role in self.specialized_roles:
            permissions.update(ROLE_PERMISSION_MAP.get(role, []))
        
        # Add delegated permissions (if within time window)
        if self.delegated_permissions:
            now = datetime.utcnow()
            if self.delegation_start <= now < self.delegation_end:
                permissions.update(self.delegated_permissions)
        
        return list(permissions)
    
    def has_permission(self, permission):
        """Check if this membership has a permission"""
        return permission in self.get_permissions()
    
    def __str__(self):
        return f"{self.user_profile.email} - {self.organization.name} ({self.org_role})"


class PermissionDelegation(Document):
    """
    Audit trail for permission delegations
    """
    
    meta = {
        'collection': 'permission_delegations',
        'indexes': [
            'organization',
            'from_user',
            'to_user',
            'status',
            'created_at',
        ],
    }
    
    delegation_id = StringField(required=True, unique=True, default=lambda: str(uuid.uuid4()))
    
    organization = ReferenceField('apps.organizations.Organization', required=True)
    from_user = ReferenceField(UserProfile, required=True)  # ORG_OWNER who delegates
    to_user = ReferenceField(UserProfile, required=True)  # Recipient
    
    permissions = ListField(StringField(), required=True)
    reason = StringField(required=True)
    
    valid_from = DateTimeField(default=datetime.utcnow)
    valid_until = DateTimeField()  # None = indefinite
    
    status = StringField(default='ACTIVE')  # ACTIVE, REVOKED, EXPIRED
    revoked_at = DateTimeField()
    revoked_by = ReferenceField(UserProfile)
    revoke_reason = StringField()
    
    # Audit
    ip_address = StringField()
    user_agent = StringField()
    
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def is_valid(self):
        """Check if delegation is still valid"""
        if self.status != 'ACTIVE':
            return False
        if self.valid_until and datetime.utcnow() >= self.valid_until:
            return False
        return True
    
    def __str__(self):
        return f"Delegation: {self.from_user.email} → {self.to_user.email}"


class APIKey(Document):
    """
    API keys for DEVELOPER role users with scopes and rate limiting
    """
    
    meta = {
        'collection': 'api_keys',
        'indexes': [
            {'fields': ['key_hash'], 'unique': True},
            'user_profile',
            'organization',
            'is_active',
            'created_at',
        ],
    }
    
    # Identification
    key_id = StringField(required=True, unique=True, default=lambda: str(uuid.uuid4()))
    user_profile = ReferenceField(UserProfile, required=True)
    organization = ReferenceField('apps.organizations.Organization', required=True)
    name = StringField(required=True, max_length=200)
    key_hash = StringField(required=True, unique=True)
    description = StringField()
    
    # Permissions & scopes
    scopes = ListField(StringField())  # e.g., ['read:projects', 'write:data_intake']
    
    # Rate limiting
    rate_limit_per_hour = IntField(default=1000)
    rate_limit_per_day = IntField(default=10000)
    
    # Approval workflow
    requires_approval = BooleanField(default=True)
    approved_by = ReferenceField(UserProfile)
    approved_at = DateTimeField()
    
    # Status
    is_active = BooleanField(default=True)
    last_used_at = DateTimeField()
    
    # Expiration
    expires_at = DateTimeField()
    
    # Audit
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    rotated_at = DateTimeField()
    
    @staticmethod
    def generate_key():
        """Generate a new API key"""
        return f"kabro_{uuid.uuid4().hex}"
    
    @staticmethod
    def hash_key(key):
        """Hash an API key for storage"""
        return hmac.new(
            b'kabro-api-key-v1',
            key.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def __str__(self):
        return f"API Key: {self.name} ({self.user_profile.email})"


class PasswordReset(Document):
    """Password reset tokens with security"""
    
    meta = {
        'collection': 'password_resets',
        'indexes': [
            {'fields': ['token'], 'unique': True},
            'user_profile',
            'created_at',
        ],
    }
    
    user_profile = ReferenceField(UserProfile, required=True)
    token = StringField(required=True, unique=True, default=lambda: str(uuid.uuid4()))
    is_used = BooleanField(default=False)
    
    created_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField(default=lambda: datetime.utcnow() + timedelta(hours=24))
    used_at = DateTimeField()
    
    def is_valid(self):
        """Check if token is still valid"""
        return not self.is_used and datetime.utcnow() < self.expires_at
    
    def __str__(self):
        return f"Reset for {self.user_profile.email}"


class AuditLog(Document):
    """
    Comprehensive audit trail for all important actions
    """
    
    meta = {
        'collection': 'audit_logs',
        'indexes': [
            'user_profile',
            'organization',
            'action',
            'resource_type',
            'created_at',
            'severity',
        ],
    }
    
    audit_id = StringField(required=True, unique=True, default=lambda: str(uuid.uuid4()))
    
    # Actor & context
    user_profile = ReferenceField(UserProfile)
    organization = ReferenceField('apps.organizations.Organization')
    
    # Action details
    action = StringField(required=True)  # e.g., 'CREATE_PROJECT', 'OVERRIDE_MRV', 'DELEGATE_PERMISSION'
    resource_type = StringField(required=True)  # e.g., 'Project', 'MRVRequest', 'PermissionDelegation'
    resource_id = StringField()
    
    description = StringField()
    changes = DictField()  # Before/after state
    
    # Security context
    ip_address = StringField()
    user_agent = StringField()
    session_id = StringField()
    
    # Severity for security events
    severity = StringField(default='INFO')  # INFO, WARNING, CRITICAL
    
    # Timestamp
    created_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"{self.action} on {self.resource_type} by {self.user_profile.email if self.user_profile else 'System'}"
