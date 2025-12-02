"""
Marketplace models
"""

from mongoengine import Document, StringField, DecimalField, ReferenceField, DateTimeField, BooleanField, ListField
from datetime import datetime


class ListingStatusChoices:
    """Listing status choices"""
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    SOLD_OUT = 'sold_out'
    
    CHOICES = [
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
        (SOLD_OUT, 'Sold Out'),
    ]


class OrderStatusChoices:
    """Order status choices"""
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    
    CHOICES = [
        (PENDING, 'Pending'),
        (CONFIRMED, 'Confirmed'),
        (SHIPPED, 'Shipped'),
        (DELIVERED, 'Delivered'),
        (CANCELLED, 'Cancelled'),
    ]


class Listing(Document):
    """Marketplace listing document"""
    credit_batch = ReferenceField('apps.registry.CreditBatch')
    seller_organization = ReferenceField('apps.organizations.Organization')
    quantity_available = DecimalField()
    unit_price = DecimalField()
    status = StringField(default=ListingStatusChoices.ACTIVE)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'listings'
    }


class Order(Document):
    """Marketplace order document"""
    listing = ReferenceField(Listing)
    buyer_organization = ReferenceField('apps.organizations.Organization')
    quantity = DecimalField()
    total_price = DecimalField()
    status = StringField(default=OrderStatusChoices.PENDING)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'orders'
    }


class TradeHistory(Document):
    """Trade history document"""
    listing = ReferenceField(Listing)
    order = ReferenceField(Order)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'trade_histories'
    }
