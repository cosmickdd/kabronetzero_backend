"""
Retirement app serializers
"""

from rest_framework import serializers


class RetirementRecordSerializer(serializers.Serializer):
    """Serializer for retirement records"""
    
    id = serializers.CharField(read_only=True)
    credit_batch_id = serializers.CharField()
    retired_by_org_id = serializers.CharField()
    quantity_retired = serializers.DecimalField(max_digits=20, decimal_places=4)
    retirement_date = serializers.DateTimeField()
    purpose = serializers.CharField()
    reference_id = serializers.CharField()
    notes = serializers.CharField(required=False)
    created_at = serializers.DateTimeField(read_only=True)


class RetirementCertificateSerializer(serializers.Serializer):
    """Serializer for retirement certificates"""
    
    id = serializers.CharField(read_only=True)
    retirement_record_id = serializers.CharField()
    certificate_number = serializers.CharField()
    serial_number = serializers.CharField()
    quantity_retired = serializers.DecimalField(max_digits=20, decimal_places=4)
    retirement_date = serializers.DateTimeField()
    organization_name = serializers.CharField()
    certificate_url = serializers.URLField()
    is_public = serializers.BooleanField()
    issued_at = serializers.DateTimeField(read_only=True)
