"""
ESG app serializers
"""

from rest_framework import serializers


class EmissionInventorySerializer(serializers.Serializer):
    """Serializer for emission inventory"""
    
    id = serializers.CharField(read_only=True)
    organization_id = serializers.CharField()
    project_id = serializers.CharField(required=False)
    report_year = serializers.IntegerField()
    report_period_start = serializers.DateTimeField(required=False)
    report_period_end = serializers.DateTimeField(required=False)
    scope_1_emissions = serializers.FloatField()
    scope_2_emissions = serializers.FloatField()
    scope_3_emissions = serializers.FloatField()
    removals = serializers.FloatField(required=False)
    offsets = serializers.FloatField(required=False)
    net_emissions = serializers.FloatField()
    reduction_target = serializers.FloatField(required=False)
    target_year = serializers.IntegerField(required=False)
    reduction_achieved = serializers.FloatField(required=False)
    data_completeness = serializers.FloatField(required=False)
    third_party_verified = serializers.BooleanField()
    verification_body = serializers.CharField(required=False)
    methodology = serializers.CharField(required=False)
    boundary_scope = serializers.CharField(required=False)
    notes = serializers.CharField(required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class ESGReportSerializer(serializers.Serializer):
    """Serializer for ESG reports"""
    
    id = serializers.CharField(read_only=True)
    organization_id = serializers.CharField()
    report_year = serializers.IntegerField()
    report_type = serializers.CharField()
    title = serializers.CharField()
    environmental_score = serializers.FloatField()
    social_score = serializers.FloatField()
    governance_score = serializers.FloatField()
    overall_score = serializers.FloatField()
    total_emissions = serializers.FloatField(required=False)
    renewable_energy_percentage = serializers.FloatField(required=False)
    waste_reduction_percentage = serializers.FloatField(required=False)
    employee_count = serializers.IntegerField(required=False)
    employee_satisfaction_score = serializers.FloatField(required=False)
    safety_incidents = serializers.IntegerField(required=False)
    diversity_percentage = serializers.FloatField(required=False)
    board_diversity_percentage = serializers.FloatField(required=False)
    women_in_leadership_percentage = serializers.FloatField(required=False)
    goals = serializers.ListField(required=False)
    commitments = serializers.ListField(required=False)
    report_url = serializers.URLField(required=False)
    report_format = serializers.CharField(required=False)
    is_published = serializers.BooleanField()
    is_verified = serializers.BooleanField()
    created_at = serializers.DateTimeField(read_only=True)
    published_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class ESGGoalSerializer(serializers.Serializer):
    """Serializer for ESG goals"""
    
    id = serializers.CharField(read_only=True)
    organization_id = serializers.CharField()
    category = serializers.CharField()
    goal_description = serializers.CharField()
    target_value = serializers.FloatField()
    target_unit = serializers.CharField()
    target_year = serializers.IntegerField()
    current_value = serializers.FloatField()
    progress_percentage = serializers.FloatField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
