"""
Marketplace app serializers
"""

from rest_framework import serializers


class ListingSerializer(serializers.Serializer):
    """Serializer for marketplace listings"""
    
    id = serializers.CharField(read_only=True)
    credit_batch_id = serializers.CharField()
    seller_organization_id = serializers.CharField()
    price_per_credit = serializers.DecimalField(max_digits=15, decimal_places=2)
    quantity_available = serializers.DecimalField(max_digits=20, decimal_places=4)
    currency = serializers.CharField()
    status = serializers.CharField()
    description = serializers.CharField(required=False)
    listed_at = serializers.DateTimeField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)


class OrderSerializer(serializers.Serializer):
    """Serializer for marketplace orders"""
    
    id = serializers.CharField(read_only=True)
    listing_id = serializers.CharField()
    buyer_organization_id = serializers.CharField()
    quantity = serializers.DecimalField(max_digits=20, decimal_places=4)
    total_price = serializers.DecimalField(max_digits=15, decimal_places=2)
    payment_status = serializers.CharField()
    delivery_status = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)
    completed_at = serializers.DateTimeField(read_only=True)
