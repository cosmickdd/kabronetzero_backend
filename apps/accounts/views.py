"""
Authentication views for Django REST Framework
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth.models import User

from apps.accounts.serializers import RegisterSerializer, LoginSerializer, UserProfileSerializer
from apps.accounts.models import UserProfile


class RegisterViewSet(viewsets.ViewSet):
    """User registration endpoint"""
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'User registered successfully'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileViewSet(viewsets.ViewSet):
    """User profile management"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        try:
            profile = UserProfile.objects.get(django_user_id=str(request.user.id))
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'User profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update current user profile"""
        try:
            profile = UserProfile.objects.get(django_user_id=str(request.user.id))
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'User profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            # Update profile fields
            if 'first_name' in request.data:
                profile.first_name = request.data['first_name']
            if 'last_name' in request.data:
                profile.last_name = request.data['last_name']
            if 'phone_number' in request.data:
                profile.phone_number = request.data['phone_number']
            if 'bio' in request.data:
                profile.bio = request.data['bio']
            if 'profile_picture_url' in request.data:
                profile.profile_picture_url = request.data['profile_picture_url']
            
            profile.save()
            return Response(UserProfileSerializer(profile).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
