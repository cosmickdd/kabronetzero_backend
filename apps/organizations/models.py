"""
Organization models
"""

from mongoengine import Document, StringField, EmailField, ListField, ReferenceField, DateTimeField
from datetime import datetime


class Organization(Document):
    """Organization document"""
    name = StringField(required=True)
    email = EmailField()
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'organizations'
    }


class OrganizationMembership(Document):
    """Organization membership document"""
    organization = ReferenceField('apps.organizations.Organization')
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
