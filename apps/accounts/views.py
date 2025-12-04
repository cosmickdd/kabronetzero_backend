"""
Comprehensive authentication views with multi-role support
Endpoints:
  - User registration (multiple types)
  - Login/logout
  - Profile management
  - Organization management
  - Admin/regulator operations
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import secrets

from apps.accounts.models import (
    UserProfile, OrganizationMembership, PermissionDelegation,
    PasswordReset, AuditLog, PlatformRoleChoices,
    OrganizationRoleChoices, SpecializedRoleChoices
)
from apps.accounts.serializers import (
    RegisterSerializer, RegisterOrgOwnerSerializer, RegisterBuyerSerializer,
    LoginSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    UserProfileSerializer, OrgContextSerializer, OrganizationDetailSerializer,
    MemberInviteSerializer, AcceptInviteSerializer, ChangeMemberRoleSerializer,
    CreateDelegationSerializer, DelegationListSerializer,
    AdminUserListSerializer, AdminUserStatusSerializer, PromoteToRegulatorSerializer
)
from apps.organizations.models import Organization, OrganizationInvitation
from apps.api.permissions import (
    IsAdmin, IsRegulator, IsNotFrozen, IsOrganizationOwner,
    IsOrganizationMember, CanManageMembers, CanAssignRoles
)


# ==================== REGISTRATION VIEWSETS ====================

class RegisterViewSet(viewsets.ViewSet):
    """User registration endpoints"""
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def create(self, request):
        """Generic user registration"""
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    'message': 'User registered successfully',
                    'user_id': str(user.id),
                    'email': user.email
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='org-owner')
    def create_org_owner(self, request):
        """Register as organization owner + create org"""
        serializer = RegisterOrgOwnerSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    'message': 'Organization owner registered successfully',
                    'user_id': str(user.id),
                    'email': user.email
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='buyer')
    def create_buyer(self, request):
        """Register as buyer"""
        serializer = RegisterBuyerSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    'message': 'Buyer registered successfully',
                    'user_id': str(user.id),
                    'email': user.email
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthViewSet(viewsets.ViewSet):
    """Authentication endpoints"""
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """Email + password login"""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(email=serializer.validated_data['email'])
                profile = UserProfile.objects.get(django_user_id=str(user.id))
                
                # Update last login
                profile.last_login = timezone.now()
                profile.save()
                
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                
                return Response(
                    {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                        'user': UserProfileSerializer(profile).data
                    },
                    status=status.HTTP_200_OK
                )
            except (User.DoesNotExist, UserProfile.DoesNotExist):
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """Logout - blacklist refresh token"""
        # In production, add refresh token to blacklist
        return Response(
            {'message': 'Logged out successfully'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def password_reset_request(self, request):
        """Request password reset"""
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(email=serializer.validated_data['email'])
            
            # Create reset token
            token = secrets.token_urlsafe(32)
            PasswordReset.objects.create(
                user=user,
                token=token,
                expires_at=timezone.now() + timezone.timedelta(hours=1)
            )
            
            return Response(
                {'message': 'Password reset link sent to email'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def password_reset_confirm(self, request):
        """Confirm password reset"""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            reset = PasswordReset.objects.get(token=serializer.validated_data['token'])
            user = reset.user
            user.set_password(serializer.validated_data['password'])
            user.save()
            
            # Mark reset as used
            reset.is_used = True
            reset.save()
            
            return Response(
                {'message': 'Password reset successfully'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileViewSet(viewsets.ViewSet):
    """User profile management"""
    permission_classes = [IsAuthenticated, IsNotFrozen]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        try:
            profile = UserProfile.objects.get(django_user_id=str(request.user.id))
            return Response(UserProfileSerializer(profile).data)
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['patch'])
    def update_me(self, request):
        """Update current user profile"""
        try:
            profile = UserProfile.objects.get(django_user_id=str(request.user.id))
            
            # Update fields if provided
            if 'phone_number' in request.data:
                profile.phone_number = request.data['phone_number']
            if 'bio' in request.data:
                profile.bio = request.data['bio']
            
            profile.save()
            
            return Response(UserProfileSerializer(profile).data)
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def org_context(self, request):
        """Get current organization context"""
        org_id = request.query_params.get('org_id')
        
        try:
            profile = UserProfile.objects.get(django_user_id=str(request.user.id))
            
            if org_id:
                # Get specific org context
                membership = OrganizationMembership.objects.get(
                    user_profile=profile,
                    organization__id=org_id,
                    is_active=True
                )
            else:
                # Get first active org context
                membership = OrganizationMembership.objects.filter(
                    user_profile=profile,
                    is_active=True
                ).first()
            
            if not membership:
                return Response(
                    {'error': 'No organization context'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(OrgContextSerializer(membership).data)
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['patch'])
    def set_org_context(self, request):
        """Change active organization context"""
        org_id = request.data.get('organization_id')
        
        try:
            profile = UserProfile.objects.get(django_user_id=str(request.user.id))
            org = Organization.objects.get(id=org_id)
            
            membership = OrganizationMembership.objects.get(
                user_profile=profile,
                organization=org,
                is_active=True
            )
            
            return Response(OrgContextSerializer(membership).data)
        except (UserProfile.DoesNotExist, Organization.DoesNotExist, OrganizationMembership.DoesNotExist):
            return Response(
                {'error': 'Invalid organization'},
                status=status.HTTP_404_NOT_FOUND
            )


# ==================== ORGANIZATION MANAGEMENT ====================

class OrganizationManagementViewSet(viewsets.ViewSet):
    """Organization member and delegation management"""
    permission_classes = [IsAuthenticated, IsNotFrozen]
    
    @action(detail=False, methods=['get'])
    def list_organizations(self, request):
        """List organizations for current user"""
        try:
            profile = UserProfile.objects.get(django_user_id=str(request.user.id))
            memberships = OrganizationMembership.objects.filter(
                user_profile=profile,
                is_active=True
            )
            
            orgs = [
                {
                    'org_id': str(m.organization.id),
                    'name': m.organization.name,
                    'type': m.organization.type,
                    'role': m.org_role,
                    'specialized_roles': m.specialized_roles,
                }
                for m in memberships
            ]
            
            return Response(orgs)
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'], url_path='invite-member')
    def invite_member(self, request):
        """Invite member to organization"""
        org_id = request.data.get('organization_id')
        serializer = MemberInviteSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                profile = UserProfile.objects.get(django_user_id=str(request.user.id))
                org = Organization.objects.get(id=org_id)
                
                # Check if requester is ORG_OWNER or ORG_MANAGER
                membership = OrganizationMembership.objects.get(
                    user_profile=profile,
                    organization=org,
                    is_active=True
                )
                
                if membership.org_role not in ['ORG_OWNER', 'ORG_MANAGER']:
                    return Response(
                        {'error': 'Only managers can invite members'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                # Create invitation
                invitation = OrganizationInvitation.objects.create(
                    organization=org,
                    email=serializer.validated_data['email'],
                    org_role=serializer.validated_data['org_role'],
                    specialized_roles=serializer.validated_data.get('specialized_roles', []),
                    invited_by=profile,
                    message=serializer.validated_data.get('message', '')
                )
                
                return Response(
                    {
                        'message': 'Invitation sent',
                        'invitation_id': str(invitation.id)
                    },
                    status=status.HTTP_201_CREATED
                )
            except (UserProfile.DoesNotExist, Organization.DoesNotExist, OrganizationMembership.DoesNotExist) as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='accept-invite')
    def accept_invite(self, request):
        """Accept organization invitation"""
        token = request.data.get('invitation_token')
        
        try:
            invitation = OrganizationInvitation.objects.get(token=token)
            profile = UserProfile.objects.get(django_user_id=str(request.user.id))
            
            if invitation.email != profile.email:
                return Response(
                    {'error': 'Invitation not for this user'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Create membership
            membership = OrganizationMembership.objects.create(
                user_profile=profile,
                organization=invitation.organization,
                org_role=invitation.org_role,
                specialized_roles=invitation.specialized_roles,
                is_active=True,
            )
            
            # Mark invitation as accepted
            invitation.is_accepted = True
            invitation.accepted_at = timezone.now()
            invitation.save()
            
            return Response(
                {'message': 'Invitation accepted'},
                status=status.HTTP_200_OK
            )
        except (OrganizationInvitation.DoesNotExist, UserProfile.DoesNotExist):
            return Response(
                {'error': 'Invalid invitation'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'], url_path='delegations')
    def list_delegations(self, request):
        """List delegations in organization"""
        org_id = request.query_params.get('organization_id')
        
        try:
            profile = UserProfile.objects.get(django_user_id=str(request.user.id))
            delegations = PermissionDelegation.objects.filter(
                from_user=profile,
                status='ACTIVE'
            )
            
            serializer = DelegationListSerializer(delegations, many=True)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'], url_path='create-delegation')
    def create_delegation(self, request):
        """Create permission delegation"""
        org_id = request.data.get('organization_id')
        serializer = CreateDelegationSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                from_profile = UserProfile.objects.get(django_user_id=str(request.user.id))
                to_user = User.objects.get(id=serializer.validated_data['to_user_id'])
                to_profile = UserProfile.objects.get(django_user_id=str(to_user.id))
                
                delegation = PermissionDelegation.objects.create(
                    from_user=from_profile,
                    to_user=to_profile,
                    permissions=serializer.validated_data['permissions'],
                    valid_until=serializer.validated_data.get('valid_until'),
                    status='ACTIVE'
                )
                
                return Response(
                    {
                        'message': 'Delegation created',
                        'delegation_id': str(delegation.id)
                    },
                    status=status.HTTP_201_CREATED
                )
            except (UserProfile.DoesNotExist, User.DoesNotExist):
                return Response(
                    {'error': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['patch'], url_path='revoke-delegation')
    def revoke_delegation(self, request):
        """Revoke permission delegation"""
        delegation_id = request.data.get('delegation_id')
        
        try:
            delegation = PermissionDelegation.objects.get(id=delegation_id)
            delegation.status = 'REVOKED'
            delegation.revoked_at = timezone.now()
            delegation.revoked_by = UserProfile.objects.get(django_user_id=str(request.user.id))
            delegation.save()
            
            return Response({'message': 'Delegation revoked'})
        except PermissionDelegation.DoesNotExist:
            return Response(
                {'error': 'Delegation not found'},
                status=status.HTTP_404_NOT_FOUND
            )


# ==================== ADMIN OPERATIONS ====================

class AdminViewSet(viewsets.ViewSet):
    """Admin-only operations"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @action(detail=False, methods=['get'])
    def list_users(self, request):
        """List all users (admin only)"""
        profiles = UserProfile.objects.all()
        serializer = AdminUserListSerializer(profiles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch'], url_path='user-status')
    def change_user_status(self, request):
        """Change user status (freeze/verify)"""
        user_id = request.data.get('user_id')
        serializer = AdminUserStatusSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                profile = UserProfile.objects.get(id=user_id)
                
                if 'is_frozen' in request.data:
                    profile.is_frozen = request.data['is_frozen']
                    profile.freeze_reason = request.data.get('freeze_reason', '')
                
                if 'is_verified' in request.data:
                    profile.is_verified = request.data['is_verified']
                
                profile.save()
                
                return Response(AdminUserListSerializer(profile).data)
            except UserProfile.DoesNotExist:
                return Response(
                    {'error': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='promote-regulator')
    def promote_to_regulator(self, request):
        """Promote user to REGULATOR role"""
        user_id = request.data.get('user_id')
        serializer = PromoteToRegulatorSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                profile = UserProfile.objects.get(id=user_id)
                profile.platform_role = PlatformRoleChoices.REGULATOR
                profile.save()
                
                # Log audit trail
                AuditLog.objects.create(
                    user_profile=UserProfile.objects.get(django_user_id=str(request.user.id)),
                    action='PROMOTE_REGULATOR',
                    resource_type='User',
                    resource_id=str(profile.id),
                    description=f'Promoted to REGULATOR: {serializer.validated_data["reason"]}'
                )
                
                return Response({'message': 'User promoted to REGULATOR'})
            except UserProfile.DoesNotExist:
                return Response(
                    {'error': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
