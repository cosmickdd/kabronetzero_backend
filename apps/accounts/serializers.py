"""
Comprehensive authentication and user serializers with multi-role support
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from apps.accounts.models import (
    UserProfile, OrganizationMembership, PermissionDelegation,
    APIKey, PasswordReset, AuditLog, PlatformRoleChoices,
    OrganizationRoleChoices, SpecializedRoleChoices, PermissionChoices
)
from apps.organizations.models import Organization, OrganizationInvitation
import uuid
from datetime import datetime, timedelta


# ==================== REGISTRATION SERIALIZERS ====================

class RegisterSerializer(serializers.Serializer):
    """Generic user registration"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    phone_number = serializers.CharField(max_length=20, required=False)
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password': 'Passwords do not match'})
        
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'Email already registered'})
        
        return data
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        
        # Create UserProfile with default ORG_MEMBER role
        profile = UserProfile.objects.create(
            django_user_id=str(user.id),
            email=validated_data['email'],
            platform_role=None,  # No platform role by default
            phone_number=validated_data.get('phone_number', ''),
            is_verified=False,
        )
        
        return user


class RegisterOrgOwnerSerializer(serializers.Serializer):
    """Register + create organization + become ORG_OWNER"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    phone_number = serializers.CharField(max_length=20, required=False)
    
    # Organization fields
    org_name = serializers.CharField(max_length=255, required=True)
    org_type = serializers.ChoiceField(choices=['corporate', 'NGO', 'farmer_collective', 'government', 'SME'], required=True)
    org_email = serializers.EmailField(required=False)
    org_phone = serializers.CharField(max_length=20, required=False)
    org_website = serializers.URLField(required=False)
    org_description = serializers.CharField(required=False)
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password': 'Passwords do not match'})
        
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'Email already registered'})
        
        if Organization.objects.filter(name=data['org_name']).exists():
            raise serializers.ValidationError({'org_name': 'Organization name already exists'})
        
        return data
    
    def create(self, validated_data):
        # Create user
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        
        # Create UserProfile
        profile = UserProfile.objects.create(
            django_user_id=str(user.id),
            email=validated_data['email'],
            phone_number=validated_data.get('phone_number', ''),
            is_verified=False,
        )
        
        # Create organization
        org = Organization.objects.create(
            name=validated_data['org_name'],
            type=validated_data['org_type'],
            email=validated_data.get('org_email', ''),
            phone_number=validated_data.get('org_phone', ''),
            website=validated_data.get('org_website', ''),
            description=validated_data.get('org_description', ''),
        )
        
        # Add user as ORG_OWNER
        OrganizationMembership.objects.create(
            user_profile=profile,
            organization=org,
            org_role=OrganizationRoleChoices.ORG_OWNER,
            is_active=True,
        )
        
        return user


class RegisterBuyerSerializer(serializers.Serializer):
    """Register as BUYER with buyer organization"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    company_name = serializers.CharField(max_length=255, required=True)
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password': 'Passwords do not match'})
        
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'Email already registered'})
        
        return data
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        
        profile = UserProfile.objects.create(
            django_user_id=str(user.id),
            email=validated_data['email'],
            is_verified=False,
        )
        
        # Create buyer organization
        org = Organization.objects.create(
            name=validated_data['company_name'],
            type='corporate',
        )
        
        # Add as ORG_OWNER + BUYER specialized role
        membership = OrganizationMembership.objects.create(
            user_profile=profile,
            organization=org,
            org_role=OrganizationRoleChoices.ORG_OWNER,
            is_active=True,
        )
        membership.specialized_roles = [SpecializedRoleChoices.BUYER]
        membership.save()
        
        return user


class LoginSerializer(serializers.Serializer):
    """Email + password login"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    
    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
            if not user.check_password(data['password']):
                raise serializers.ValidationError({'password': 'Invalid credentials'})
        except User.DoesNotExist:
            raise serializers.ValidationError({'email': 'User not found'})
        
        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    """Request password reset"""
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('User with this email not found')
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Confirm password reset with token"""
    token = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password': 'Passwords do not match'})
        
        # Validate token exists and not expired
        try:
            reset = PasswordReset.objects.get(token=data['token'])
            if reset.is_expired():
                raise serializers.ValidationError({'token': 'Reset token has expired'})
            if reset.is_used:
                raise serializers.ValidationError({'token': 'Reset token already used'})
        except PasswordReset.DoesNotExist:
            raise serializers.ValidationError({'token': 'Invalid reset token'})
        
        return data


# ==================== PROFILE & CONTEXT SERIALIZERS ====================

class UserProfileSerializer(serializers.Serializer):
    """User profile with roles and organizations"""
    id = serializers.SerializerMethodField()
    email = serializers.EmailField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    phone_number = serializers.CharField()
    platform_role = serializers.CharField(allow_null=True)
    is_frozen = serializers.BooleanField()
    is_verified = serializers.BooleanField()
    last_login = serializers.DateTimeField()
    organizations = serializers.SerializerMethodField()
    
    def get_id(self, obj):
        return str(obj.id)
    
    def get_first_name(self, obj):
        try:
            user = User.objects.get(id=obj.django_user_id)
            return user.first_name
        except:
            return ''
    
    def get_last_name(self, obj):
        try:
            user = User.objects.get(id=obj.django_user_id)
            return user.last_name
        except:
            return ''
    
    def get_organizations(self, obj):
        memberships = OrganizationMembership.objects.filter(user_profile=obj, is_active=True)
        return [
            {
                'org_id': str(m.organization.id),
                'org_name': m.organization.name,
                'org_role': m.org_role,
                'specialized_roles': m.specialized_roles,
                'permissions': m.get_permissions(),
            }
            for m in memberships
        ]


class OrgContextSerializer(serializers.Serializer):
    """Organization context for user"""
    organization_id = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    org_role = serializers.SerializerMethodField()
    specialized_roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    
    def get_organization_id(self, obj):
        return str(obj.organization.id)
    
    def get_organization_name(self, obj):
        return obj.organization.name
    
    def get_org_role(self, obj):
        return obj.org_role
    
    def get_specialized_roles(self, obj):
        return obj.specialized_roles or []
    
    def get_permissions(self, obj):
        return obj.get_permissions()


# ==================== ORGANIZATION MANAGEMENT SERIALIZERS ====================

class OrganizationDetailSerializer(serializers.Serializer):
    """Organization details"""
    id = serializers.SerializerMethodField()
    name = serializers.CharField()
    type = serializers.CharField()
    email = serializers.EmailField()
    phone_number = serializers.CharField()
    website = serializers.URLField()
    description = serializers.CharField()
    is_active = serializers.BooleanField()
    is_verified = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    
    def get_id(self, obj):
        return str(obj.id)


class MemberInviteSerializer(serializers.Serializer):
    """Invite member to organization"""
    email = serializers.EmailField(required=True)
    org_role = serializers.ChoiceField(
        choices=['ORG_OWNER', 'ORG_MANAGER', 'ORG_MEMBER'],
        required=True
    )
    specialized_roles = serializers.ListField(
        child=serializers.ChoiceField(choices=['VALIDATOR', 'BUYER', 'DEVELOPER']),
        required=False,
        allow_empty=True
    )
    message = serializers.CharField(required=False, allow_blank=True)


class AcceptInviteSerializer(serializers.Serializer):
    """Accept organization invitation"""
    invitation_token = serializers.CharField(required=True)


class ChangeMemberRoleSerializer(serializers.Serializer):
    """Change organization member role"""
    org_role = serializers.ChoiceField(
        choices=['ORG_OWNER', 'ORG_MANAGER', 'ORG_MEMBER'],
        required=True
    )
    specialized_roles = serializers.ListField(
        child=serializers.ChoiceField(choices=['VALIDATOR', 'BUYER', 'DEVELOPER']),
        required=False,
        allow_empty=True
    )


# ==================== DELEGATION SERIALIZERS ====================

class CreateDelegationSerializer(serializers.Serializer):
    """Create permission delegation"""
    to_user_id = serializers.CharField(required=True)
    permissions = serializers.ListField(
        child=serializers.CharField(),
        required=True
    )
    valid_until = serializers.DateTimeField(required=False)
    reason = serializers.CharField(required=False, allow_blank=True)


class DelegationListSerializer(serializers.Serializer):
    """List delegations"""
    id = serializers.SerializerMethodField()
    from_user_email = serializers.SerializerMethodField()
    to_user_email = serializers.SerializerMethodField()
    permissions = serializers.ListField(child=serializers.CharField())
    valid_from = serializers.DateTimeField()
    valid_until = serializers.DateTimeField()
    status = serializers.CharField()
    
    def get_id(self, obj):
        return str(obj.id)
    
    def get_from_user_email(self, obj):
        return obj.from_user.email
    
    def get_to_user_email(self, obj):
        return obj.to_user.email


# ==================== ADMIN SERIALIZERS ====================

class AdminUserListSerializer(serializers.Serializer):
    """List users for admin"""
    id = serializers.SerializerMethodField()
    email = serializers.CharField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    platform_role = serializers.CharField()
    is_frozen = serializers.BooleanField()
    is_verified = serializers.BooleanField()
    last_login = serializers.DateTimeField()
    
    def get_id(self, obj):
        return str(obj.id)
    
    def get_first_name(self, obj):
        try:
            user = User.objects.get(id=obj.django_user_id)
            return user.first_name
        except:
            return ''
    
    def get_last_name(self, obj):
        try:
            user = User.objects.get(id=obj.django_user_id)
            return user.last_name
        except:
            return ''


class AdminUserStatusSerializer(serializers.Serializer):
    """Admin: change user status"""
    is_frozen = serializers.BooleanField(required=False)
    is_verified = serializers.BooleanField(required=False)
    freeze_reason = serializers.CharField(required=False, allow_blank=True)


class PromoteToRegulatorSerializer(serializers.Serializer):
    """Admin: promote user to REGULATOR"""
    reason = serializers.CharField(required=True)


# ==================== ADDITIONAL REGISTRATION SERIALIZERS ====================

class AcceptInvitationSerializer(serializers.Serializer):
    """Accept organization invitation"""
    token = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, min_length=8, required=False)
    full_name = serializers.CharField(max_length=255, required=False)
    
    def create(self, validated_data):
        # Implementation for accepting invitation
        pass


class RegisterValidatorSerializer(serializers.Serializer):
    """Create validator account (admin only)"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    full_name = serializers.CharField(max_length=255, required=True)
    
    def create(self, validated_data):
        # Implementation for creating validator
        pass


class CreateRegulatorSerializer(serializers.Serializer):
    """Create regulator account (admin only)"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    full_name = serializers.CharField(max_length=255, required=True)
    
    def create(self, validated_data):
        # Implementation for creating regulator
        pass


class UserProfileResponseSerializer(serializers.Serializer):
    """User profile response"""
    id = serializers.CharField()
    email = serializers.EmailField()
    full_name = serializers.CharField()
    global_role = serializers.CharField()
    is_verified = serializers.BooleanField()
    active_org_id = serializers.CharField(allow_null=True)


class InviteMemberSerializer(serializers.Serializer):
    """Invite member to organization"""
    email = serializers.EmailField(required=True)
    role_in_org = serializers.CharField(required=True)
    message = serializers.CharField(required=False, allow_blank=True)
    
    def create(self, validated_data):
        # Implementation for inviting member
        pass


class SetOrgContextSerializer(serializers.Serializer):
    """Set active organization context"""
    organization_id = serializers.CharField(required=True)
    
    def create(self, validated_data):
        # Implementation for setting org context
        pass


class OrganizationMembershipSerializer(serializers.Serializer):
    """Organization membership"""
    id = serializers.CharField()
    user_id = serializers.CharField()
    organization_id = serializers.CharField()
    role_in_org = serializers.CharField()
    is_active = serializers.BooleanField()

