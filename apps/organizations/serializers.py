"""
Organizations serializers
"""

from rest_framework import serializers
from organizations.models import (
    Organization, OrganizationMembership, OrganizationInvitation,
    OrganizationMembershipRoleChoices, Location, OrganizationIntegration
)


class LocationSerializer(serializers.Serializer):
    """Serializer for location embedded document"""
    
    country = serializers.CharField()
    state = serializers.CharField(required=False)
    city = serializers.CharField(required=False)
    latitude = serializers.CharField(required=False)
    longitude = serializers.CharField(required=False)
    postal_code = serializers.CharField(required=False)
    address = serializers.CharField(required=False)


class OrganizationSerializer(serializers.Serializer):
    """Serializer for organizations"""
    
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=255)
    slug = serializers.SlugField(required=False)
    type = serializers.CharField()
    email = serializers.EmailField()
    phone_number = serializers.CharField(required=False)
    website = serializers.URLField(required=False)
    location = LocationSerializer(required=False)
    registration_id = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    logo_url = serializers.URLField(required=False)
    is_verified = serializers.BooleanField()
    is_active = serializers.BooleanField()
    treasury_wallet_address = serializers.CharField(required=False)
    default_currency = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class OrganizationMembershipSerializer(serializers.Serializer):
    """Serializer for organization memberships"""
    
    id = serializers.CharField(read_only=True)
    organization_id = serializers.CharField(required=False)
    user_email = serializers.EmailField()
    role = serializers.ChoiceField(choices=OrganizationMembershipRoleChoices.CHOICES)
    permissions = serializers.ListField(child=serializers.CharField(), required=False)
    is_active = serializers.BooleanField()
    invited_by = serializers.CharField(required=False)
    accepted_at = serializers.DateTimeField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class OrganizationInvitationSerializer(serializers.Serializer):
    """Serializer for organization invitations"""
    
    id = serializers.CharField(read_only=True)
    organization_id = serializers.CharField()
    email = serializers.EmailField()
    token = serializers.CharField(read_only=True)
    role = serializers.ChoiceField(choices=OrganizationMembershipRoleChoices.CHOICES)
    invited_by = serializers.CharField(required=False)
    is_accepted = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    expires_at = serializers.DateTimeField()


class OrganizationIntegrationSerializer(serializers.Serializer):
    """Serializer for organization integrations"""
    
    id = serializers.CharField(read_only=True)
    organization_id = serializers.CharField()
    integration_type = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField(required=False)
    config = serializers.DictField()
    is_active = serializers.BooleanField()
    last_used_at = serializers.DateTimeField(read_only=True)
    success_count = serializers.CharField()
    failure_count = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
