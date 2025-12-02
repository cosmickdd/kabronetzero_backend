"""
Accounts app models - User profiles, roles, permissions, API keys
"""

from django.contrib.auth.models import User
from mongoengine import (
    Document, StringField, EmailField, BooleanField, DateTimeField,
    ReferenceField, ListField, DictField, SequenceField
)
from datetime import datetime
import uuid
import hmac
import hashlib


class UserRoleChoices:
    """User role constants"""
    ADMIN = 'ADMIN'
    ORG_OWNER = 'ORG_OWNER'
    ORG_MEMBER = 'ORG_MEMBER'
    VALIDATOR = 'VALIDATOR'
    REGULATOR = 'REGULATOR'
    BUYER = 'BUYER'
    DEVELOPER = 'DEVELOPER'

    CHOICES = [
        (ADMIN, 'Administrator'),
        (ORG_OWNER, 'Organization Owner'),
        (ORG_MEMBER, 'Organization Member'),
        (VALIDATOR, 'MRV Validator'),
        (REGULATOR, 'Regulator'),
        (BUYER, 'Carbon Buyer'),
        (DEVELOPER, 'Developer'),
    ]


class UserProfile(Document):
    """Extended user profile stored in MongoDB"""
    
    meta = {
        'collection': 'user_profiles',
        'indexes': [
            'django_user_id',
            'email',
            'role',
        ],
    }
    
    django_user_id = StringField(required=True, unique=True)  # Link to Django User
    email = EmailField(required=True, unique=True)
    first_name = StringField(max_length=100)
    last_name = StringField(max_length=100)
    phone_number = StringField()
    
    # Role in the system
    role = StringField(
        choices=UserRoleChoices.CHOICES,
        default=UserRoleChoices.ORG_MEMBER
    )
    
    # Profile metadata
    profile_picture_url = StringField()
    bio = StringField()
    is_active = BooleanField(default=True)
    is_verified = BooleanField(default=False)
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"{self.email} ({self.role})"


class APIKey(Document):
    """API keys for DEVELOPER role users"""
    
    meta = {
        'collection': 'api_keys',
        'indexes': [
            ('key_hash', 'unique'),
            'user_profile',
            'is_active',
            'created_at',
        ],
    }
    
    user_profile = ReferenceField(UserProfile, required=True)
    name = StringField(required=True, max_length=200)
    key_hash = StringField(required=True, unique=True)  # HMAC hash of the actual key
    description = StringField()
    
    # Permissions for the API key
    scopes = ListField(StringField())  # e.g., ['read:projects', 'write:data_intake', 'read:registry']
    
    # Rate limiting
    rate_limit_per_hour = StringField(default='1000')
    
    # Status
    is_active = BooleanField(default=True)
    last_used_at = DateTimeField()
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField()  # Optional expiration
    
    @staticmethod
    def generate_key():
        """Generate a new API key"""
        return f"kabro_{uuid.uuid4().hex}"
    
    @staticmethod
    def hash_key(key):
        """Hash an API key for storage"""
        return hmac.new(
            b'kabro-api-key',
            key.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def __str__(self):
        return f"{self.name} ({self.user_profile.email})"


class PasswordReset(Document):
    """Password reset tokens"""
    
    meta = {
        'collection': 'password_resets',
        'indexes': [
            ('token', 'unique'),
            'user_profile',
            'created_at',
        ],
    }
    
    user_profile = ReferenceField(UserProfile, required=True)
    token = StringField(required=True, unique=True)
    is_used = BooleanField(default=False)
    
    created_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField(required=True)
    
    def is_valid(self):
        """Check if token is still valid"""
        return not self.is_used and datetime.utcnow() < self.expires_at
    
    def __str__(self):
        return f"Reset for {self.user_profile.email}"


class AuditLog(Document):
    """Audit trail for all important actions"""
    
    meta = {
        'collection': 'audit_logs',
        'indexes': [
            'user_profile',
            'action',
            'resource_type',
            'created_at',
        ],
    }
    
    user_profile = ReferenceField(UserProfile)
    action = StringField(required=True)  # e.g., 'CREATE_PROJECT', 'APPROVE_MRV'
    resource_type = StringField(required=True)  # e.g., 'Project', 'MRVRequest'
    resource_id = StringField()  # MongoDB ObjectId as string
    
    description = StringField()
    changes = DictField()  # Track what changed
    ip_address = StringField()
    user_agent = StringField()
    
    created_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"{self.action} on {self.resource_type} by {self.user_profile.email if self.user_profile else 'System'}"
