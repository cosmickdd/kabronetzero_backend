"""
Data Intake app serializers
"""

from rest_framework import serializers
from apps.data_intake.models import DataSource, DataPoint, DataAggregation, DataSourceTypeChoices, MetricTypeChoices


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
    count = serializers.IntegerField()
    sum_value = serializers.DecimalField(max_digits=20, decimal_places=6)
    avg_value = serializers.DecimalField(max_digits=20, decimal_places=6)
    min_value = serializers.DecimalField(max_digits=20, decimal_places=6)
    max_value = serializers.DecimalField(max_digits=20, decimal_places=6)
    unit = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)
