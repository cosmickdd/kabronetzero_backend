"""
Organization models - Companies, NGOs, farmer collectives, government entities
"""

from mongoengine import (
    Document, StringField, EmailField, ListField, ReferenceField, DateTimeField,
    EmbeddedDocument, EmbeddedDocumentField, BooleanField, DictField, DecimalField
)
from datetime import datetime


class OrganizationTypeChoices:
    """Organization type constants"""
    CORPORATE = 'corporate'
    NGO = 'ngo'
    FARMER_COLLECTIVE = 'farmer_collective'
    GOVERNMENT = 'government'
    SME = 'sme'
    OTHER = 'other'
    
    CHOICES = [
        (CORPORATE, 'Corporate'),
        (NGO, 'NGO'),
        (FARMER_COLLECTIVE, 'Farmer Collective'),
        (GOVERNMENT, 'Government'),
        (SME, 'Small & Medium Enterprise'),
        (OTHER, 'Other'),
    ]


class OrganizationMembershipRoleChoices:
    """Role choices for organization membership"""
    OWNER = 'OWNER'
    ADMIN = 'ADMIN'
    MANAGER = 'MANAGER'
    MEMBER = 'MEMBER'
    VIEWER = 'VIEWER'
    DEVELOPER = 'DEVELOPER'
    
    CHOICES = [
        (OWNER, 'Owner'),
        (ADMIN, 'Admin'),
        (MANAGER, 'Manager'),
        (MEMBER, 'Member'),
        (VIEWER, 'Viewer'),
        (DEVELOPER, 'Developer'),
    ]


class Location(EmbeddedDocument):
    """Location embedded document"""
    country = StringField(required=True)
    state = StringField()
    city = StringField()
    latitude = DecimalField()
    longitude = DecimalField()
    postal_code = StringField()
    address = StringField()


class Organization(Document):
    """
    Organization document - Companies, NGOs, farmer collectives, government entities
    """
    
    meta = {
        'collection': 'organizations',
        'indexes': [
            'name',
            'email',
            'type',
            'is_active',
            'created_at',
        ],
    }
    
    # Basic info
    name = StringField(required=True, max_length=200)
    type = StringField(
        choices=OrganizationTypeChoices.CHOICES,
        required=True
    )
    email = EmailField(unique=True)
    phone_number = StringField()
    website = StringField()
    description = StringField()
    
    # Registration details
    registration_id = StringField()  # Company registration number
    gstin = StringField()  # GST ID (India specific)
    tax_id = StringField()  # Tax identification number
    
    # Location
    location = EmbeddedDocumentField(Location)
    
    # Status & verification
    is_active = BooleanField(default=True)
    is_verified = BooleanField(default=False)
    verification_date = DateTimeField()
    verified_by = ReferenceField('apps.accounts.UserProfile')
    
    # Metrics
    total_projects = StringField(default='0')
    total_credits_issued = DecimalField(default=0)
    total_credits_retired = DecimalField(default=0)
    
    # Metadata
    metadata = DictField()  # For storing extra information
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"{self.name} ({self.type})"


class OrganizationMembership(Document):
    """
    Organization membership - links users to organizations with specific roles
    """
    
    meta = {
        'collection': 'organization_memberships',
        'indexes': [
            'organization',
            'user_profile',
            'role',
            'is_active',
            'created_at',
        ],
    }
    
    organization = ReferenceField(Organization, required=True)
    user_profile = ReferenceField('apps.accounts.UserProfile', required=True)
    
    # Role within this organization
    role = StringField(
        choices=OrganizationMembershipRoleChoices.CHOICES,
        required=True,
        default=OrganizationMembershipRoleChoices.MEMBER
    )
    
    # Permissions flags
    can_create_projects = BooleanField(default=False)
    can_edit_projects = BooleanField(default=False)
    can_submit_data = BooleanField(default=False)
    can_manage_members = BooleanField(default=False)
    can_view_reports = BooleanField(default=True)
    
    # Status
    is_active = BooleanField(default=True)
    invited_by = ReferenceField('apps.accounts.UserProfile')
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    accepted_at = DateTimeField()
    
    def __str__(self):
        return f"{self.user_profile.email} - {self.organization.name} ({self.role})"


class OrganizationInvitation(Document):
    """
    Organization invitation - pending invitations to join organizations
    """
    
    meta = {
        'collection': 'organization_invitations',
        'indexes': [
            'organization',
            'email',
            'is_accepted',
            'created_at',
        ],
    }
    
    organization = ReferenceField(Organization, required=True)
    email = EmailField(required=True)
    role = StringField(
        choices=OrganizationMembershipRoleChoices.CHOICES,
        required=True,
        default=OrganizationMembershipRoleChoices.MEMBER
    )
    
    invited_by = ReferenceField('apps.accounts.UserProfile', required=True)
    token = StringField(unique=True)  # Invitation token
    
    is_accepted = BooleanField(default=False)
    is_expired = BooleanField(default=False)
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    accepted_at = DateTimeField()
    expires_at = DateTimeField()
    
    def is_valid(self):
        """Check if invitation is still valid"""
        return not self.is_accepted and not self.is_expired and datetime.utcnow() < self.expires_at
    
    def __str__(self):
        return f"Invitation to {self.email} for {self.organization.name}"


class OrganizationIntegration(Document):
    """
    Organization integrations - webhook configs, API integrations, etc.
    """
    
    meta = {
        'collection': 'organization_integrations',
        'indexes': [
            'organization',
            'integration_type',
            'is_active',
        ],
    }
    
    organization = ReferenceField(Organization, required=True)
    integration_type = StringField(required=True)  # e.g., 'WEBHOOK', 'API', 'IOT_GATEWAY'
    name = StringField(required=True)
    
    # Configuration
    config = DictField()  # Integration-specific config (webhooks, API endpoints, etc.)
    is_active = BooleanField(default=True)
    
    # Status & logging
    last_used_at = DateTimeField()
    error_count = StringField(default='0')
    last_error = StringField()
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"{self.organization.name} - {self.integration_type}"
