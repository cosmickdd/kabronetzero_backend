"""
Tokenization app serializers
"""

from rest_framework import serializers
from apps.tokenization.models import TokenizationJob, TokenizationEvent, TokenizationStatusChoices, BlockchainChainChoices


class TokenizationEventSerializer(serializers.Serializer):
    """Serializer for tokenization events"""
    
    id = serializers.CharField(read_only=True)
    tokenization_job_id = serializers.CharField()
    event_type = serializers.CharField()
    event_name = serializers.CharField()
    tx_hash = serializers.CharField()
    block_number = serializers.IntegerField()
    log_index = serializers.IntegerField()
    from_address = serializers.CharField()
    to_address = serializers.CharField()
    token_id = serializers.CharField()
    amount = serializers.CharField()
    event_data = serializers.JSONField()
    timestamp = serializers.DateTimeField(read_only=True)


class TokenizationJobSerializer(serializers.Serializer):
    """Serializer for tokenization jobs"""
    
    id = serializers.CharField(read_only=True)
    credit_batch_id = serializers.CharField()
    project_id = serializers.CharField()
    chain = serializers.ChoiceField(choices=BlockchainChainChoices.CHOICES)
    contract_address = serializers.CharField(required=False)
    status = serializers.ChoiceField(choices=TokenizationStatusChoices.CHOICES)
    external_job_id = serializers.CharField(required=False)
    tx_hash = serializers.CharField(required=False)
    token_id = serializers.CharField(required=False)
    token_address = serializers.CharField(required=False)
    error_message = serializers.CharField(required=False)
    retry_count = serializers.IntegerField()
    metadata = serializers.JSONField(required=False)
    created_at = serializers.DateTimeField(read_only=True)
    started_at = serializers.DateTimeField(read_only=True)
    completed_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
