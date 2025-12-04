"""
Organization views
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from apps.organizations.models import (
    Organization, OrganizationMembership, OrganizationInvitation
)
from apps.organizations.serializers import (
    OrganizationSerializer, OrganizationMembershipSerializer,
    OrganizationInvitationSerializer
)
from apps.api.permissions import IsOrganizationOwner, IsAdmin


class OrganizationViewSet(viewsets.ModelViewSet):
    """ViewSet for organizations"""
    permission_classes = [IsAuthenticated]
    serializer_class = OrganizationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'is_active', 'is_verified']
    search_fields = ['name', 'email']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get organizations visible to user"""
        user = self.request.user
        # For now, return all active organizations
        # In production, filter by membership
        return Organization.objects()
    
    def perform_create(self, serializer):
        """Create organization"""
        org_data = serializer.validated_data
        # Create using MongoEngine
        org = Organization(
            name=org_data.get('name'),
            type=org_data.get('type'),
            email=org_data.get('email'),
            phone_number=org_data.get('phone_number'),
            website=org_data.get('website'),
            description=org_data.get('description'),
        )
        org.save()
        
        # Add creator as owner
        OrganizationMembership.objects.create(
            organization=org,
            user_email=self.request.user.email,
            role='OWNER',
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsOrganizationOwner])
    def add_member(self, request, pk=None):
        """Add member to organization"""
        org = Organization.objects.get(id=pk)
        
        email = request.data.get('email')
        role = request.data.get('role', 'VIEWER')
        
        if OrganizationMembership.objects.filter(
            organization=org, user_email=email
        ).exists():
            return Response(
                {'error': 'User already a member'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        membership = OrganizationMembership(
            organization=org,
            user_email=email,
            role=role,
            invited_by=request.user.email,
        )
        membership.save()
        
        return Response(
            OrganizationMembershipSerializer(membership).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get organization members"""
        org = Organization.objects.get(id=pk)
        memberships = OrganizationMembership.objects.filter(organization=org, is_active=True)
        serializer = OrganizationMembershipSerializer(memberships, many=True)
        return Response(serializer.data)


class OrganizationMembershipViewSet(viewsets.ModelViewSet):
    """ViewSet for organization memberships"""
    permission_classes = [IsAuthenticated]
    serializer_class = OrganizationMembershipSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['organization', 'is_active', 'role']
    
    def get_queryset(self):
        """Get memberships for current user"""
        user = self.request.user
        return OrganizationMembership.objects.filter(user_email=user.email)
    
    @action(detail=True, methods=['post'], permission_classes=[IsOrganizationOwner])
    def remove_member(self, request, pk=None):
        """Remove member from organization"""
        membership = OrganizationMembership.objects.get(id=pk)
        membership.is_active = False
        membership.save()
        
        return Response({'message': 'Member removed'})


class OrganizationInvitationViewSet(viewsets.ModelViewSet):
    """ViewSet for organization invitations"""
    permission_classes = [IsAuthenticated]
    serializer_class = OrganizationInvitationSerializer
    
    def get_queryset(self):
        """Get invitations for current user"""
        user = self.request.user
        return OrganizationInvitation.objects.filter(email=user.email)
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept organization invitation"""
        invitation = OrganizationInvitation.objects.get(id=pk)
        
        if not invitation.is_valid():
            return Response(
                {'error': 'Invitation is expired or already accepted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create membership
        membership = OrganizationMembership(
            organization=invitation.organization,
            user_email=request.user.email,
            role=invitation.role,
            accepted_at=__import__('datetime').datetime.utcnow(),
        )
        membership.save()
        
        invitation.is_accepted = True
        invitation.accepted_at = __import__('datetime').datetime.utcnow()
        invitation.save()
        
        return Response({'message': 'Invitation accepted'})
