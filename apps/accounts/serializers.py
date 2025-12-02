"""
Accounts app serializers
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from accounts.models import UserProfile, APIKey, AuditLog


class UserProfileSerializer(serializers.Serializer):
    """Serializer for user profile"""
    
    id = serializers.CharField(read_only=True)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    phone_number = serializers.CharField(required=False)
    bio = serializers.CharField(required=False)
    profile_picture_url = serializers.URLField(required=False)
    role = serializers.CharField()
    is_active = serializers.BooleanField()
    is_verified = serializers.BooleanField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class RegisterSerializer(serializers.Serializer):
    """Serializer for user registration"""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(required=False)
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class APIKeySerializer(serializers.Serializer):
    """Serializer for API keys"""
    
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=200)
    key_hash = serializers.CharField(read_only=True)
    description = serializers.CharField(required=False)
    scopes = serializers.ListField(child=serializers.CharField())
    rate_limit_per_hour = serializers.IntegerField()
    is_active = serializers.BooleanField()
    last_used_at = serializers.DateTimeField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    expires_at = serializers.DateTimeField(required=False)


class AuditLogSerializer(serializers.Serializer):
    """Serializer for audit logs"""
    
    id = serializers.CharField(read_only=True)
    user_email = serializers.EmailField()
    action = serializers.CharField()
    resource_type = serializers.CharField()
    resource_id = serializers.CharField()
    details = serializers.JSONField()
    ip_address = serializers.CharField()
    user_agent = serializers.CharField()
    timestamp = serializers.DateTimeField(read_only=True)
