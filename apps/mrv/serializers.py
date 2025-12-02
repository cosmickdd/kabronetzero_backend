"""
MRV app serializers
"""

from rest_framework import serializers
from apps.mrv.models import MRVRequest, MRVAssessment, MRVAuditLog, MRVStatusChoices, AssessmentDecisionChoices


class MRVRequestSerializer(serializers.Serializer):
    """Serializer for MRV requests"""
    
    id = serializers.CharField(read_only=True)
    project_id = serializers.CharField()
    requested_by_email = serializers.EmailField()
    status = serializers.ChoiceField(choices=MRVStatusChoices.CHOICES)
    reporting_period_start = serializers.DateTimeField(required=False)
    reporting_period_end = serializers.DateTimeField(required=False)
    documentation_urls = serializers.ListField(child=serializers.URLField(), required=False)
    evidence_files = serializers.ListField(child=serializers.CharField(), required=False)
    initial_estimate_credits = serializers.DecimalField(max_digits=20, decimal_places=4, required=False)
    submitted_at = serializers.DateTimeField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class MRVAssessmentSerializer(serializers.Serializer):
    """Serializer for MRV assessments"""
    
    id = serializers.CharField(read_only=True)
    mrv_request_id = serializers.CharField()
    project_id = serializers.CharField()
    validator_email = serializers.EmailField()
    validator_organization = serializers.CharField(required=False)
    decision = serializers.ChoiceField(choices=AssessmentDecisionChoices.CHOICES)
    recommended_credits = serializers.DecimalField(max_digits=20, decimal_places=4, required=False)
    risk_score = serializers.FloatField(required=False)
    anomalies_detected = serializers.ListField(required=False)
    assessment_notes = serializers.CharField(required=False)
    assessment_report_url = serializers.URLField(required=False)
    calculation_methodology = serializers.CharField(required=False)
    submitted_at = serializers.DateTimeField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class MRVAuditLogSerializer(serializers.Serializer):
    """Serializer for MRV audit logs"""
    
    id = serializers.CharField(read_only=True)
    mrv_request_id = serializers.CharField(required=False)
    mrv_assessment_id = serializers.CharField(required=False)
    action = serializers.CharField()
    performed_by = serializers.CharField()
    performer_role = serializers.CharField()
    details = serializers.JSONField()
    timestamp = serializers.DateTimeField(read_only=True)
