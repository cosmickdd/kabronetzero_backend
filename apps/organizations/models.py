"""
Organization models
"""

from mongoengine import Document, StringField, EmailField, ListField, ReferenceField, DateTimeField, EmbeddedDocument, EmbeddedDocumentField
from datetime import datetime


class OrganizationMembershipRoleChoices:
    """Role choices for organization membership"""
    OWNER = 'owner'
    ADMIN = 'admin'
    MEMBER = 'member'
    VIEWER = 'viewer'
    
    CHOICES = [
        (OWNER, 'Owner'),
        (ADMIN, 'Admin'),
        (MEMBER, 'Member'),
        (VIEWER, 'Viewer'),
    ]


class Location(EmbeddedDocument):
    """Location embedded document"""
    country = StringField()
    state = StringField()
    city = StringField()
    latitude = StringField()
    longitude = StringField()
    postal_code = StringField()
    address = StringField()


class Organization(Document):
    """Organization document"""
    name = StringField(required=True)
    email = EmailField()
    location = EmbeddedDocumentField(Location)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'organizations'
    }


class OrganizationMembership(Document):
    """Organization membership document"""
    organization = ReferenceField('apps.organizations.Organization')
    role = StringField(default=OrganizationMembershipRoleChoices.MEMBER)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'organization_memberships'
    }


class OrganizationInvitation(Document):
    """Organization invitation document"""
    organization = ReferenceField('apps.organizations.Organization')
    email = EmailField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'organization_invitations'
    }


class OrganizationIntegration(Document):
    """Organization integration document"""
    organization = ReferenceField('apps.organizations.Organization')
    integration_type = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'organization_integrations'
    }
