"""
Marketplace and retirement serializers
"""

from rest_framework import serializers
from apps.marketplace.models import (
    Listing, Order, TradeHistory, ListingStatusChoices, OrderStatusChoices
)
from apps.retirement.models import (
    RetirementRecord, RetirementCertificate, RetirementPurposeChoices
)


class ListingSerializer(serializers.Serializer):
    """Serializer for marketplace listings"""
    
    id = serializers.CharField(read_only=True)
    credit_batch_id = serializers.CharField()
    seller_organization_id = serializers.CharField()
    quantity_available = serializers.DecimalField(max_digits=20, decimal_places=4)
    quantity_sold = serializers.DecimalField(max_digits=20, decimal_places=4, read_only=True)
    unit_price = serializers.DecimalField(max_digits=15, decimal_places=2)
    currency = serializers.CharField()
    description = serializers.CharField(required=False)
    terms_and_conditions = serializers.CharField(required=False)
    status = serializers.ChoiceField(choices=ListingStatusChoices.CHOICES)
    is_active = serializers.BooleanField()
    tags = serializers.ListField(child=serializers.CharField(), required=False)
    min_order_quantity = serializers.DecimalField(max_digits=20, decimal_places=4)
    max_order_quantity = serializers.DecimalField(max_digits=20, decimal_places=4, required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class OrderSerializer(serializers.Serializer):
    """Serializer for marketplace orders"""
    
    id = serializers.CharField(read_only=True)
    listing_id = serializers.CharField()
    buyer_organization_id = serializers.CharField()
    quantity = serializers.DecimalField(max_digits=20, decimal_places=4)
    unit_price = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    currency = serializers.CharField()
    status = serializers.ChoiceField(choices=OrderStatusChoices.CHOICES)
    payment_method = serializers.CharField(required=False)
    payment_reference = serializers.CharField(required=False)
    payment_confirmed_at = serializers.DateTimeField(read_only=True)
    delivery_completed_at = serializers.DateTimeField(read_only=True)
    notes = serializers.CharField(required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class RetirementRecordSerializer(serializers.Serializer):
    """Serializer for retirement records"""
    
    id = serializers.CharField(read_only=True)
    credit_batch_id = serializers.CharField()
    quantity_retired = serializers.DecimalField(max_digits=20, decimal_places=4)
    retired_by_org_id = serializers.CharField()
    retired_by_user_email = serializers.EmailField(required=False)
    retirement_date = serializers.DateTimeField()
    purpose = serializers.ChoiceField(choices=RetirementPurposeChoices.CHOICES)
    reference_id = serializers.CharField(read_only=True)
    certificate_issued_date = serializers.DateTimeField(read_only=True)
    scope = serializers.CharField(required=False)
    reporting_year = serializers.CharField(required=False)
    supporting_documents = serializers.ListField(child=serializers.CharField(), required=False)
    notes = serializers.CharField(required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class RetirementCertificateSerializer(serializers.Serializer):
    """Serializer for retirement certificates"""
    
    id = serializers.CharField(read_only=True)
    retirement_record_id = serializers.CharField()
    certificate_number = serializers.CharField(read_only=True)
    certificate_url = serializers.URLField(read_only=True)
    organization_name = serializers.CharField()
    carbon_category = serializers.CharField()
    quantity_retired = serializers.DecimalField(max_digits=20, decimal_places=4)
    unit = serializers.CharField()
    retirement_date = serializers.DateTimeField()
    purpose = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)
