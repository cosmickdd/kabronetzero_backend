"""
MRV and data intake serializers
"""

from rest_framework import serializers
from mrv.models import (
    MRVRequest, MRVAssessment, MRVAuditLog, MRVStatusChoices,
    AssessmentDecisionChoices
)
from data_intake.models import (
    DataSource, DataPoint, DataAggregation, DataSourceTypeChoices,
    MetricTypeChoices
)


class MRVRequestSerializer(serializers.Serializer):
    """Serializer for MRV requests"""
    
    id = serializers.CharField(read_only=True)
    project_id = serializers.CharField()
    status = serializers.ChoiceField(choices=MRVStatusChoices.CHOICES)
    requested_by_email = serializers.EmailField()
    reporting_period_start = serializers.DateTimeField(required=False)
    reporting_period_end = serializers.DateTimeField(required=False)
    documentation_urls = serializers.ListField(child=serializers.URLField(), required=False)
    evidence_files = serializers.ListField(child=serializers.CharField(), required=False)
    submitted_at = serializers.DateTimeField(read_only=True)
    initial_estimate_credits = serializers.DecimalField(max_digits=20, decimal_places=4, required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class MRVAssessmentSerializer(serializers.Serializer):
    """Serializer for MRV assessments"""
    
    id = serializers.CharField(read_only=True)
    mrv_request_id = serializers.CharField()
    validator_email = serializers.EmailField()
    validator_organization = serializers.CharField(required=False)
    comments = serializers.CharField(required=False)
    risk_score = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    data_quality_score = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    is_compliant_with_standard = serializers.BooleanField(required=False)
    compliance_notes = serializers.CharField(required=False)
    decision = serializers.ChoiceField(choices=AssessmentDecisionChoices.CHOICES)
    recommended_credits = serializers.DecimalField(max_digits=20, decimal_places=4, required=False)
    assessment_started_at = serializers.DateTimeField(read_only=True)
    decided_at = serializers.DateTimeField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class DataSourceSerializer(serializers.Serializer):
    """Serializer for data sources"""
    
    id = serializers.CharField(read_only=True)
    project_id = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField(required=False)
    type = serializers.ChoiceField(choices=DataSourceTypeChoices.CHOICES)
    metadata = serializers.DictField(required=False)
    is_active = serializers.BooleanField()
    last_data_received = serializers.DateTimeField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class DataPointSerializer(serializers.Serializer):
    """Serializer for data points"""
    
    id = serializers.CharField(read_only=True)
    data_source_id = serializers.CharField()
    project_id = serializers.CharField()
    metric_type = serializers.ChoiceField(choices=MetricTypeChoices.CHOICES)
    value = serializers.DecimalField(max_digits=20, decimal_places=6)
    unit = serializers.CharField()
    raw_payload = serializers.DictField(required=False)
    is_validated = serializers.BooleanField()
    validation_status = serializers.CharField(required=False)
    validation_notes = serializers.CharField(required=False)
    timestamp = serializers.DateTimeField()
    created_at = serializers.DateTimeField(read_only=True)


class DataAggregationSerializer(serializers.Serializer):
    """Serializer for data aggregations"""
    
    id = serializers.CharField(read_only=True)
    project_id = serializers.CharField()
    metric_type = serializers.CharField()
    period = serializers.CharField()
    period_start = serializers.DateTimeField()
    period_end = serializers.DateTimeField()
    count = serializers.CharField()
    sum_value = serializers.DecimalField(max_digits=20, decimal_places=4, required=False)
    avg_value = serializers.DecimalField(max_digits=20, decimal_places=4, required=False)
    min_value = serializers.DecimalField(max_digits=20, decimal_places=4, required=False)
    max_value = serializers.DecimalField(max_digits=20, decimal_places=4, required=False)
    unit = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)
