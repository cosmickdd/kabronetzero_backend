"""
Registry and tokenization serializers
"""

from rest_framework import serializers
from apps.registry.models import CreditBatch, CreditTransactionLog, BatchStatusChoices, CreditStatusChoices
from apps.tokenization.models import TokenizationJob, TokenizationStatusChoices, BlockchainChainChoices


class CreditBatchSerializer(serializers.Serializer):
    """Serializer for credit batches"""
    
    id = serializers.CharField(read_only=True)
    batch_id = serializers.CharField()
    project_id = serializers.CharField()
    mrv_request_id = serializers.CharField(required=False)
    carbon_category_id = serializers.CharField()
    total_credits = serializers.DecimalField(max_digits=20, decimal_places=4)
    issue_date = serializers.DateTimeField()
    credit_vintage_start = serializers.DateTimeField(required=False)
    credit_vintage_end = serializers.DateTimeField(required=False)
    status = serializers.ChoiceField(choices=BatchStatusChoices.CHOICES)
    credits_available = serializers.DecimalField(max_digits=20, decimal_places=4, required=False)
    credits_reserved = serializers.DecimalField(max_digits=20, decimal_places=4, read_only=True)
    credits_retired = serializers.DecimalField(max_digits=20, decimal_places=4, read_only=True)
    issuing_organization_id = serializers.CharField()
    current_holder_id = serializers.CharField(required=False)
    is_tokenized = serializers.BooleanField()
    token_contract_address = serializers.CharField(required=False)
    token_id = serializers.CharField(required=False)
    is_locked = serializers.BooleanField()
    lock_reason = serializers.CharField(required=False)
    locked_at = serializers.DateTimeField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class CreditTransactionLogSerializer(serializers.Serializer):
    """Serializer for credit transaction logs"""
    
    id = serializers.CharField(read_only=True)
    batch_id = serializers.CharField()
    transaction_type = serializers.CharField()
    from_org_id = serializers.CharField(required=False)
    to_org_id = serializers.CharField(required=False)
    quantity = serializers.DecimalField(max_digits=20, decimal_places=4)
    reference_id = serializers.CharField(required=False)
    notes = serializers.CharField(required=False)
    timestamp = serializers.DateTimeField(read_only=True)


class TokenizationJobSerializer(serializers.Serializer):
    """Serializer for tokenization jobs"""
    
    id = serializers.CharField(read_only=True)
    credit_batch_id = serializers.CharField()
    status = serializers.ChoiceField(choices=TokenizationStatusChoices.CHOICES)
    chain = serializers.ChoiceField(choices=BlockchainChainChoices.CHOICES)
    external_job_id = serializers.CharField(required=False)
    tx_hash = serializers.CharField(required=False)
    contract_address = serializers.CharField(required=False)
    token_id = serializers.CharField(required=False)
    error_message = serializers.CharField(required=False)
    retry_count = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    started_at = serializers.DateTimeField(read_only=True)
    completed_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
