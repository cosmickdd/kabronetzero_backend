"""
Registration and authentication Views for multi-tenant system
Implements 5 registration flows + login + org management
"""

from rest_framework import status, views
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ViewSet
from django.utils import timezone
from apps.accounts.models import CustomUser
from apps.organizations.models import Organization, OrganizationMembership, OrganizationInvitation
from apps.accounts.serializers_new import (
    RegisterOrgOwnerSerializer, RegisterBuyerSerializer,
    AcceptInvitationSerializer, RegisterValidatorSerializer,
    CreateRegulatorSerializer, LoginSerializer, UserProfileResponseSerializer,
    InviteMemberSerializer, SetOrgContextSerializer, OrganizationMembershipSerializer
)
from apps.api.permissions_new import (
    IsOrgOwner, IsOrgOwnerOrManager, IsAdmin,
    IsRegulatorOrAdmin
)




# ==================== REGISTRATION ENDPOINTS ====================

class RegisterOrgOwnerView(views.APIView):
    """
    POST /api/v1/auth/register/org-owner/
    Creates organization owner account
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterOrgOwnerSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.save()
        
        # Get user's membership
        membership = OrganizationMembership.objects.filter(user=user).first()
        
        return Response({
            'status': 'success',
            'message': 'Organization owner account created successfully',
            'user': {
                'id': str(user.id),
                'email': user.email,
                'full_name': user.full_name,
                'global_role': user.global_role,
                'active_org_id': str(membership.organization.id) if membership else None
            },
            'organization': {
                'id': str(membership.organization.id),
                'name': membership.organization.name,
                'type': membership.organization.type
            } if membership else None
        }, status=status.HTTP_201_CREATED)


class RegisterBuyerView(views.APIView):
    """
    POST /api/v1/auth/register/buyer/
    Creates buyer account with buyer organization
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterBuyerSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.save()
        
        # Get user's membership
        membership = OrganizationMembership.objects.filter(user=user).first()
        
        return Response({
            'status': 'success',
            'message': 'Buyer account created successfully',
            'user': {
                'id': str(user.id),
                'email': user.email,
                'full_name': user.full_name,
                'global_role': user.global_role,
                'active_org_id': str(membership.organization.id) if membership else None
            },
            'organization': {
                'id': str(membership.organization.id),
                'name': membership.organization.name,
                'type': 'buyer_org'
            } if membership else None
        }, status=status.HTTP_201_CREATED)


class AcceptInvitationView(views.APIView):
    """
    POST /api/v1/auth/accept-invitation/
    Accept organization invitation to join or create account
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = AcceptInvitationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.save()
        
        # Get user's membership to the org they just joined
        membership = OrganizationMembership.objects.filter(user=user).latest('created_at')
        
        return Response({
            'status': 'success',
            'message': 'Invitation accepted successfully',
            'user': {
                'id': str(user.id),
                'email': user.email,
                'full_name': user.full_name,
                'global_role': user.global_role
            },
            'membership': {
                'organization_id': str(membership.organization.id),
                'organization_name': membership.organization.name,
                'role_in_org': membership.role_in_org,
                'is_active': membership.is_active
            }
        }, status=status.HTTP_201_CREATED)


class RegisterValidatorView(views.APIView):
    """
    POST /api/v1/auth/register/validator/
    Admin-only: Create validator account
    """
    permission_classes = [IsAdmin]
    
    def post(self, request):
        serializer = RegisterValidatorSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.save()
        
        return Response({
            'status': 'success',
            'message': 'Validator account created successfully',
            'user': {
                'id': str(user.id),
                'email': user.email,
                'full_name': user.full_name,
                'global_role': user.global_role,
                'is_verified': user.is_verified
            }
        }, status=status.HTTP_201_CREATED)


class RegisterRegulatorView(views.APIView):
    """
    POST /api/v1/auth/register/regulator/
    Admin-only: Create regulator account
    """
    permission_classes = [IsAdmin]
    
    def post(self, request):
        serializer = CreateRegulatorSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.save()
        
        return Response({
            'status': 'success',
            'message': 'Regulator account created successfully',
            'user': {
                'id': str(user.id),
                'email': user.email,
                'full_name': user.full_name,
                'global_role': user.global_role,
                'is_verified': user.is_verified
            }
        }, status=status.HTTP_201_CREATED)


# ==================== LOGIN & TOKEN ====================

class LoginView(views.APIView):
    """
    POST /api/v1/auth/login/
    Email + password login
    Returns JWT with custom claims
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.create(serializer.validated_data)
        user = data['user']
        
        # Build response
        return Response({
            'access': data['access'],
            'refresh': data['refresh'],
            'user': {
                'id': str(user.id),
                'email': user.email,
                'full_name': user.full_name,
                'global_role': user.global_role,
                'is_verified': user.is_verified,
                'active_org_id': user.active_org_id,
                'organizations': list(
                    user.get_memberships().values(
                        'organization__id',
                        'organization__name',
                        'organization__type',
                        'role_in_org'
                    )
                )
            }
        }, status=status.HTTP_200_OK)


# ==================== USER PROFILE ====================

class UserProfileView(views.APIView):
    """
    GET /api/v1/auth/me/ - Get current user profile
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserProfileResponseSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        """
        PUT /api/v1/auth/me/ - Update user profile
        """
        user = request.user
        
        # Update allowed fields
        if 'full_name' in request.data:
            user.full_name = request.data['full_name']
        
        if 'email' in request.data:
            new_email = request.data['email']
            if CustomUser.objects.exclude(id=user.id).filter(email=new_email).exists():
                return Response(
                    {'email': 'Email already in use'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.email = new_email
            user.is_verified = False  # Mark as unverified until email confirmed
        
        user.save()
        
        serializer = UserProfileResponseSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ==================== ORGANIZATION CONTEXT ====================

class OrganizationListView(views.APIView):
    """
    GET /api/v1/auth/organizations/
    List user's organizations
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        memberships = OrganizationMembership.objects.filter(
            user=request.user,
            is_active=True
        ).select_related('organization')
        
        data = []
        for membership in memberships:
            data.append({
                'id': str(membership.organization.id),
                'name': membership.organization.name,
                'type': membership.organization.type,
                'role_in_org': membership.role_in_org,
                'is_active': membership.is_active,
                'created_at': membership.created_at,
                'is_active_org': membership.organization.id == request.user.active_org_id
            })
        
        return Response({'organizations': data}, status=status.HTTP_200_OK)


class OrganizationSetActiveView(views.APIView):
    """
    POST /api/v1/auth/organizations/set-active/
    Switch active organization context
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = SetOrgContextSerializer(
            data=request.data,
            context={'user': request.user}
        )
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        membership = serializer.save()
        
        return Response({
            'status': 'success',
            'active_org_id': str(membership.organization.id),
            'organization': {
                'id': str(membership.organization.id),
                'name': membership.organization.name,
                'type': membership.organization.type,
                'role_in_org': membership.role_in_org
            }
        }, status=status.HTTP_200_OK)


# ==================== ORGANIZATION MEMBER MANAGEMENT ====================

class OrganizationMemberInviteView(views.APIView):
    """
    POST /api/v1/organizations/{org_id}/members/invite/
    ORG_OWNER/MANAGER invites new member
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        org_id = request.headers.get('X-Org-Id') or request.query_params.get('org_id')
        
        if not org_id:
            return Response(
                {'error': 'Organization ID required (X-Org-Id header or org_id query param)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check permissions
        membership = OrganizationMembership.objects.filter(
            user=request.user,
            organization_id=org_id,
            role_in_org__in=['ORG_OWNER', 'ORG_MANAGER'],
            is_active=True
        ).first()
        
        if not membership:
            return Response(
                {'error': 'You must be ORG_OWNER or ORG_MANAGER to invite members'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            organization = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            return Response(
                {'error': 'Organization not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create invitation
        serializer = InviteMemberSerializer(
            data=request.data,
            context={'organization': organization, 'user': request.user}
        )
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        invitation = serializer.save()
        
        return Response({
            'status': 'success',
            'message': 'Invitation sent successfully',
            'invitation': {
                'token': invitation.token,
                'email': invitation.email,
                'role_in_org': invitation.role_in_org,
                'expires_at': invitation.expires_at
            }
        }, status=status.HTTP_201_CREATED)


class OrganizationMemberListView(views.APIView):
    """
    GET /api/v1/organizations/{org_id}/members/
    List organization members
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        org_id = request.headers.get('X-Org-Id') or request.query_params.get('org_id')
        
        if not org_id:
            return Response(
                {'error': 'Organization ID required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check membership
        is_member = OrganizationMembership.objects.filter(
            user=request.user,
            organization_id=org_id,
            is_active=True
        ).exists()
        
        if not is_member:
            return Response(
                {'error': 'You are not a member of this organization'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        members = OrganizationMembership.objects.filter(
            organization_id=org_id,
            is_active=True
        ).select_related('user').values(
            'id',
            'user__id',
            'user__email',
            'user__full_name',
            'role_in_org',
            'created_at',
            'is_active'
        )
        
        return Response({
            'members': list(members),
            'total': members.count()
        }, status=status.HTTP_200_OK)


class OrganizationMemberRemoveView(views.APIView):
    """
    POST /api/v1/organizations/{org_id}/members/{member_id}/remove/
    ORG_OWNER removes member
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        org_id = request.headers.get('X-Org-Id') or request.query_params.get('org_id')
        member_id = request.data.get('member_id')
        
        if not org_id or not member_id:
            return Response(
                {'error': 'Organization ID and member ID required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check requester is ORG_OWNER
        is_owner = OrganizationMembership.objects.filter(
            user=request.user,
            organization_id=org_id,
            role_in_org='ORG_OWNER',
            is_active=True
        ).exists()
        
        if not is_owner:
            return Response(
                {'error': 'Only ORG_OWNER can remove members'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get member
        member_membership = OrganizationMembership.objects.filter(
            id=member_id,
            organization_id=org_id
        ).first()
        
        if not member_membership:
            return Response(
                {'error': 'Member not found in organization'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Don't allow removing the only ORG_OWNER
        other_owners = OrganizationMembership.objects.filter(
            organization_id=org_id,
            role_in_org='ORG_OWNER',
            is_active=True
        ).exclude(id=member_id)
        
        if member_membership.role_in_org == 'ORG_OWNER' and not other_owners.exists():
            return Response(
                {'error': 'Cannot remove the only ORG_OWNER'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        member_membership.is_active = False
        member_membership.save()
        
        return Response({
            'status': 'success',
            'message': 'Member removed from organization'
        }, status=status.HTTP_200_OK)


class OrganizationMemberRoleUpdateView(views.APIView):
    """
    PUT /api/v1/organizations/{org_id}/members/{member_id}/role/
    ORG_OWNER updates member role
    """
    permission_classes = [IsAuthenticated]
    
    def put(self, request):
        org_id = request.headers.get('X-Org-Id') or request.query_params.get('org_id')
        member_id = request.data.get('member_id')
        new_role = request.data.get('role_in_org')
        
        if not org_id or not member_id or not new_role:
            return Response(
                {'error': 'Organization ID, member ID, and new role required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check requester is ORG_OWNER
        is_owner = OrganizationMembership.objects.filter(
            user=request.user,
            organization_id=org_id,
            role_in_org='ORG_OWNER',
            is_active=True
        ).exists()
        
        if not is_owner:
            return Response(
                {'error': 'Only ORG_OWNER can update member roles'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get member
        member_membership = OrganizationMembership.objects.filter(
            id=member_id,
            organization_id=org_id
        ).first()
        
        if not member_membership:
            return Response(
                {'error': 'Member not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update role
        member_membership.role_in_org = new_role
        member_membership.save()
        
        return Response({
            'status': 'success',
            'message': 'Member role updated',
            'membership': {
                'id': str(member_membership.id),
                'user_id': str(member_membership.user.id),
                'role_in_org': member_membership.role_in_org
            }
        }, status=status.HTTP_200_OK)

