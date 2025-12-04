"""
Comprehensive registration and authentication serializers for multi-tenant system
Supports: ORG_OWNER, ORG_MEMBER/MANAGER/DEVELOPER (via invite), BUYER, VALIDATOR (admin), REGULATOR (admin)
"""

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from apps.accounts.models import (
    CustomUser, PlatformRoleChoices, OrganizationRoleChoices,
    PermissionChoices, ROLE_PERMISSION_MAP
)
from apps.organizations.models import Organization, OrganizationMembership, OrganizationInvitation
from django.utils import timezone
import uuid


# ==================== ORG OWNER REGISTRATION ====================

class OrganizationInputSerializer(serializers.Serializer):
    """Sub-serializer for organization creation during registration"""
    name = serializers.CharField(max_length=255, required=True)
    type = serializers.ChoiceField(
        choices=['industry', 'buyer_org', 'validator_org'],
        required=True
    )
    country = serializers.CharField(max_length=100, required=True)
    state = serializers.CharField(max_length=100, required=False)
    city = serializers.CharField(max_length=100, required=False)
    website = serializers.URLField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)


class RegisterOrgOwnerSerializer(serializers.Serializer):
    """
    Register as Organization Owner
    Creates: CustomUser + Organization + OrganizationMembership
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=10, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    full_name = serializers.CharField(max_length=255, required=True)
    organization = OrganizationInputSerializer(required=True)
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password': 'Passwords do not match'})
        
        if CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'Email already registered'})
        
        return data
    
    def create(self, validated_data):
        org_data = validated_data.pop('organization')
        
        # 1. Create CustomUser with NORMAL_USER role
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
            global_role=PlatformRoleChoices.NORMAL_USER,
            is_verified=False
        )
        
        # 2. Create Organization
        organization = Organization.objects.create(
            name=org_data['name'],
            type=org_data['type'],
            country=org_data['country'],
            state=org_data.get('state', ''),
            city=org_data.get('city', ''),
            website=org_data.get('website', ''),
            description=org_data.get('description', ''),
            created_by=user
        )
        
        # 3. Create OrganizationMembership with ORG_OWNER role
        membership = OrganizationMembership.objects.create(
            user=user,
            organization=organization,
            role_in_org=OrganizationRoleChoices.ORG_OWNER,
            is_active=True
        )
        
        # Set user's active organization
        user.active_org_id = str(organization.id)
        user.save()
        
        return user


# ==================== BUYER REGISTRATION ====================

class RegisterBuyerSerializer(serializers.Serializer):
    """
    Register as Buyer
    Creates: CustomUser + Buyer Organization + OrganizationMembership
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=10, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    full_name = serializers.CharField(max_length=255, required=True)
    organization = OrganizationInputSerializer(required=True)
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password': 'Passwords do not match'})
        
        if CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'Email already registered'})
        
        # Ensure org type is buyer
        if data['organization']['type'] != 'buyer_org':
            data['organization']['type'] = 'buyer_org'
        
        return data
    
    def create(self, validated_data):
        org_data = validated_data.pop('organization')
        
        # 1. Create CustomUser
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
            global_role=PlatformRoleChoices.NORMAL_USER,
            is_verified=False
        )
        
        # 2. Create Buyer Organization
        organization = Organization.objects.create(
            name=org_data['name'],
            type='buyer_org',
            country=org_data['country'],
            state=org_data.get('state', ''),
            city=org_data.get('city', ''),
            website=org_data.get('website', ''),
            description=org_data.get('description', ''),
            created_by=user
        )
        
        # 3. Create OrganizationMembership with BUYER role
        membership = OrganizationMembership.objects.create(
            user=user,
            organization=organization,
            role_in_org=OrganizationRoleChoices.BUYER,
            is_active=True
        )
        
        user.active_org_id = str(organization.id)
        user.save()
        
        return user


# ==================== INVITATION-BASED REGISTRATION ====================

class AcceptInvitationSerializer(serializers.Serializer):
    """
    Accept organization invitation to register/join org
    If user doesn't exist, creates CustomUser
    """
    invite_token = serializers.CharField(required=True)
    full_name = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(write_only=True, min_length=10, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password': 'Passwords do not match'})
        
        # Check invite exists and not expired/consumed
        try:
            self.invite = OrganizationInvitation.objects.get(
                token=data['invite_token'],
                is_consumed=False,
                expires_at__gt=timezone.now()
            )
        except OrganizationInvitation.DoesNotExist:
            raise serializers.ValidationError({'invite_token': 'Invalid or expired invitation'})
        
        return data
    
    def create(self, validated_data):
        invite = self.invite
        
        # 1. Get or create CustomUser
        user, created = CustomUser.objects.get_or_create(
            email=invite.email,
            defaults={
                'full_name': validated_data['full_name'],
                'global_role': PlatformRoleChoices.NORMAL_USER,
                'is_verified': False
            }
        )
        
        if created:
            user.set_password(validated_data['password'])
            user.save()
        
        # 2. Create OrganizationMembership with invited role
        membership = OrganizationMembership.objects.create(
            user=user,
            organization=invite.organization,
            role_in_org=invite.role_in_org,
            is_active=True
        )
        
        # 3. Mark invitation as consumed
        invite.is_consumed = True
        invite.consumed_at = timezone.now()
        invite.consumed_by = user
        invite.save()
        
        # Set active org if first org
        if not user.active_org_id:
            user.active_org_id = str(invite.organization.id)
            user.save()
        
        return user


# ==================== ADMIN ENDPOINTS ====================

class RegisterValidatorSerializer(serializers.Serializer):
    """
    Admin endpoint to create VALIDATOR
    Validator has global_role = VALIDATOR
    """
    email = serializers.EmailField(required=True)
    full_name = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(write_only=True, min_length=10, required=False)
    organization_name = serializers.CharField(max_length=255, required=False)
    
    def validate(self, data):
        if CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'Email already registered'})
        return data
    
    def create(self, validated_data):
        # Generate temporary password if not provided
        password = validated_data.get('password', str(uuid.uuid4())[:20])
        
        # Create CustomUser with VALIDATOR global role
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=password,
            full_name=validated_data['full_name'],
            global_role=PlatformRoleChoices.VALIDATOR,
            is_verified=True  # Admins create pre-verified
        )
        
        # Optionally create/link to validator organization
        org_name = validated_data.get('organization_name', 'Validator Organization')
        # TODO: Link to validator org if exists
        
        return user


class CreateRegulatorSerializer(serializers.Serializer):
    """
    Admin endpoint to create REGULATOR
    """
    email = serializers.EmailField(required=True)
    full_name = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(write_only=True, min_length=10, required=False)
    agency_name = serializers.CharField(max_length=255, required=False)
    
    def validate(self, data):
        if CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'Email already registered'})
        return data
    
    def create(self, validated_data):
        password = validated_data.get('password', str(uuid.uuid4())[:20])
        
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=password,
            full_name=validated_data['full_name'],
            global_role=PlatformRoleChoices.REGULATOR,
            is_verified=True
        )
        
        return user


# ==================== LOGIN & TOKEN ====================

class LoginSerializer(serializers.Serializer):
    """
    Email + password login
    Returns JWT tokens + user context
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    active_org_id = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        user = authenticate(
            username=data['email'],
            password=data['password']
        )
        
        if not user:
            raise serializers.ValidationError({'password': 'Invalid email or password'})
        
        if not user.is_active:
            raise serializers.ValidationError({'email': 'Account is inactive'})
        
        if user.is_frozen:
            raise serializers.ValidationError({'email': f'Account frozen: {user.freeze_reason}'})
        
        data['user'] = user
        return data
    
    def create(self, validated_data):
        user = validated_data['user']
        user.last_login = timezone.now()
        user.save()
        
        # Get or create tokens
        refresh = RefreshToken.for_user(user)
        
        # Add custom claims to access token
        access = refresh.access_token
        access['global_role'] = user.global_role
        
        # Set active org if provided or use first membership
        active_org_id = validated_data.get('active_org_id')
        if active_org_id:
            # Verify user is member of this org
            membership = OrganizationMembership.objects.filter(
                user=user,
                organization_id=active_org_id,
                is_active=True
            ).first()
            if membership:
                access['active_org_id'] = str(membership.organization.id)
                access['org_role'] = membership.role_in_org
        else:
            # Use first active membership
            membership = OrganizationMembership.objects.filter(
                user=user,
                is_active=True
            ).order_by('-created_at').first()
            if membership:
                access['active_org_id'] = str(membership.organization.id)
                access['org_role'] = membership.role_in_org
        
        return {
            'access': str(access),
            'refresh': str(refresh),
            'user': user
        }


# ==================== USER RESPONSES ====================

class OrganizationMembershipSerializer(serializers.Serializer):
    """Serializer for user's organization context"""
    id = serializers.CharField()
    name = serializers.CharField()
    type = serializers.CharField()
    role_in_org = serializers.CharField()
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField()


class UserProfileResponseSerializer(serializers.Serializer):
    """Response serializer for user profile with organizations"""
    id = serializers.CharField()
    email = serializers.EmailField()
    full_name = serializers.CharField()
    global_role = serializers.CharField()
    is_active = serializers.BooleanField()
    is_verified = serializers.BooleanField()
    is_frozen = serializers.BooleanField()
    organizations = serializers.SerializerMethodField()
    active_org = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()
    last_login = serializers.DateTimeField()
    
    def get_organizations(self, user):
        memberships = OrganizationMembership.objects.filter(
            user=user,
            is_active=True
        )
        return [
            {
                'id': str(m.organization.id),
                'name': m.organization.name,
                'type': m.organization.type,
                'role_in_org': m.role_in_org,
                'is_active': m.is_active,
                'created_at': m.created_at
            }
            for m in memberships
        ]
    
    def get_active_org(self, user):
        if not user.active_org_id:
            return None
        
        membership = OrganizationMembership.objects.filter(
            user=user,
            organization_id=user.active_org_id,
            is_active=True
        ).first()
        
        if membership:
            return {
                'id': str(membership.organization.id),
                'name': membership.organization.name,
                'type': membership.organization.type,
                'role_in_org': membership.role_in_org,
                'permissions': ROLE_PERMISSION_MAP.get(membership.role_in_org, [])
            }
        return None


# ==================== INVITATION MANAGEMENT ====================

class InviteMemberSerializer(serializers.Serializer):
    """
    ORG_OWNER/MANAGER invites member to organization
    """
    email = serializers.EmailField(required=True)
    role_in_org = serializers.ChoiceField(
        choices=['ORG_OWNER', 'ORG_MANAGER', 'ORG_MEMBER', 'DEVELOPER', 'BUYER'],
        required=True
    )
    message = serializers.CharField(required=False, allow_blank=True)
    expires_at = serializers.DateTimeField(required=False)
    
    def create(self, validated_data):
        # This is called from view with organization context
        organization = self.context.get('organization')
        inviter = self.context.get('user')
        
        # Create invitation
        expires_at = validated_data.get('expires_at', timezone.now() + timezone.timedelta(days=30))
        
        invitation = OrganizationInvitation.objects.create(
            organization=organization,
            email=validated_data['email'],
            role_in_org=validated_data['role_in_org'],
            message=validated_data.get('message', ''),
            invited_by=inviter,
            expires_at=expires_at,
            token=str(uuid.uuid4())
        )
        
        # TODO: Send email with invitation link
        
        return invitation


# ==================== ORG CONTEXT SWITCHING ====================

class SetOrgContextSerializer(serializers.Serializer):
    """
    User switches active organization
    """
    organization_id = serializers.CharField(required=True)
    
    def validate(self, data):
        user = self.context.get('user')
        organization_id = data['organization_id']
        
        # Verify user is member of this org
        membership = OrganizationMembership.objects.filter(
            user=user,
            organization_id=organization_id,
            is_active=True
        ).first()
        
        if not membership:
            raise serializers.ValidationError('You are not a member of this organization')
        
        data['membership'] = membership
        return data
    
    def create(self, validated_data):
        user = self.context.get('user')
        membership = validated_data['membership']
        
        user.active_org_id = str(membership.organization.id)
        user.save()
        
        return membership
