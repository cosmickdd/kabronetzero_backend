"""
Projects serializers
"""

from rest_framework import serializers
from projects.models import (
    Project, CarbonCategory, ProjectMethodology, ProjectStatusChoices,
    CarbonCategoryChoices, StandardChoices
)


class CarbonCategorySerializer(serializers.Serializer):
    """Serializer for carbon categories"""
    
    id = serializers.CharField(read_only=True)
    code = serializers.ChoiceField(choices=CarbonCategoryChoices.CHOICES)
    name = serializers.CharField()
    description = serializers.CharField(required=False)
    default_methodology = serializers.CharField(required=False)
    typical_credit_duration = serializers.CharField(required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class ProjectMethodologySerializer(serializers.Serializer):
    """Serializer for project methodologies"""
    
    id = serializers.CharField(read_only=True)
    project_id = serializers.CharField()
    methodology_code = serializers.CharField()
    standard = serializers.ChoiceField(choices=StandardChoices.CHOICES)
    description = serializers.CharField(required=False)
    documentation_url = serializers.URLField(required=False)
    parameters = serializers.DictField(required=False)
    version = serializers.CharField()
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class ProjectLocationSerializer(serializers.Serializer):
    """Serializer for project location"""
    country = serializers.CharField()
    state = serializers.CharField(required=False)
    city = serializers.CharField(required=False)
    area_sq_km = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)


class ProjectSerializer(serializers.Serializer):
    """Serializer for carbon projects"""
    
    id = serializers.CharField(read_only=True)
    organization_id = serializers.CharField()
    name = serializers.CharField(max_length=255)
    slug = serializers.SlugField(required=False)
    description = serializers.CharField(required=False)
    carbon_category_id = serializers.CharField()
    carbon_category_code = serializers.SerializerMethodField(read_only=True)
    baseline_emissions = serializers.DecimalField(max_digits=20, decimal_places=4, required=False)
    target_reduction = serializers.DecimalField(max_digits=20, decimal_places=4, required=False)
    location = ProjectLocationSerializer(required=False)
    status = serializers.ChoiceField(choices=ProjectStatusChoices.CHOICES)
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    credit_vintage_start = serializers.DateTimeField(required=False)
    credit_vintage_end = serializers.DateTimeField(required=False)
    monitoring_plan_url = serializers.URLField(required=False)
    has_methodology = serializers.BooleanField()
    total_credits_to_issue = serializers.DecimalField(max_digits=20, decimal_places=4, required=False)
    issued_credits = serializers.DecimalField(max_digits=20, decimal_places=4, read_only=True)
    retired_credits = serializers.DecimalField(max_digits=20, decimal_places=4, read_only=True)
    submitted_at = serializers.DateTimeField(read_only=True)
    approved_at = serializers.DateTimeField(read_only=True)
    rejection_reason = serializers.CharField(required=False)
    tags = serializers.ListField(child=serializers.CharField(), required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    def get_carbon_category_code(self, obj):
        if hasattr(obj, 'carbon_category') and obj.carbon_category:
            return obj.carbon_category.code
        return None


class ProjectDetailSerializer(ProjectSerializer):
    """Detailed project serializer with related data"""
    
    methodologies = ProjectMethodologySerializer(many=True, read_only=True)
