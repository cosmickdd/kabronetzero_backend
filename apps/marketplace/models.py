"""
Marketplace models - Carbon credit trading, listings, and orders
"""

from mongoengine import (
    Document, StringField, DecimalField, ReferenceField, DateTimeField, 
    BooleanField, ListField, DictField, IntField
)
from datetime import datetime


class ListingStatusChoices:
    """Listing status constants"""
    OPEN = 'OPEN'
    PARTIALLY_FILLED = 'PARTIALLY_FILLED'
    FILLED = 'FILLED'
    CANCELLED = 'CANCELLED'
    EXPIRED = 'EXPIRED'
    
    CHOICES = [
        (OPEN, 'Open'),
        (PARTIALLY_FILLED, 'Partially Filled'),
        (FILLED, 'Filled'),
        (CANCELLED, 'Cancelled'),
        (EXPIRED, 'Expired'),
    ]


class OrderStatusChoices:
    """Order status constants"""
    PENDING_PAYMENT = 'PENDING_PAYMENT'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    CANCELLED = 'CANCELLED'
    
    CHOICES = [
        (PENDING_PAYMENT, 'Pending Payment'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
        (CANCELLED, 'Cancelled'),
    ]


class Listing(Document):
    """
    Marketplace listing - seller offers carbon credits for sale
    """
    
    meta = {
        'collection': 'listings',
        'indexes': [
            'credit_batch',
            'seller_organization',
            'status',
            'unit_price',
            'carbon_category',
            'created_at',
        ],
    }
    
    # Listing identification
    listing_id = StringField(required=True, unique=True)
    
    # Credit source
    credit_batch = ReferenceField('apps.registry.CreditBatch', required=True)
    carbon_category = ReferenceField('apps.projects.CarbonCategory', required=True)
    
    # Seller
    seller_organization = ReferenceField('apps.organizations.Organization', required=True)
    seller_contact_email = StringField()
    
    # Quantity & pricing
    quantity = DecimalField(required=True)  # Available credits
    quantity_sold = DecimalField(default=0)
    quantity_remaining = DecimalField(required=True)
    
    unit_price = DecimalField(required=True)  # Price per credit
    currency = StringField(default='INR')  # INR, USD, EUR, etc.
    
    # Listing details
    description = StringField()
    tags = ListField(StringField())
    
    # Status
    status = StringField(
        choices=ListingStatusChoices.CHOICES,
        default=ListingStatusChoices.OPEN
    )
    
    # Filters & categories
    location = StringField()  # Project location
    project_type = StringField()
    certification_standard = StringField()
    
    # Listing lifecycle
    listed_date = DateTimeField(default=datetime.utcnow)
    expiration_date = DateTimeField()
    
    # Metadata
    metadata = DictField()
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"{self.listing_id} - {self.quantity_remaining}/{self.quantity} credits @ {self.unit_price} {self.currency}"


class Order(Document):
    """
    Marketplace order - buyer purchases credits from a listing
    """
    
    meta = {
        'collection': 'orders',
        'indexes': [
            'listing',
            'buyer_organization',
            'status',
            'created_at',
            'completed_at',
        ],
    }
    
    # Order identification
    order_id = StringField(required=True, unique=True)
    
    # Listing & credit source
    listing = ReferenceField(Listing, required=True)
    credit_batch = ReferenceField('apps.registry.CreditBatch', required=True)
    
    # Buyer
    buyer_organization = ReferenceField('apps.organizations.Organization', required=True)
    buyer_contact_email = StringField()
    
    # Transaction details
    quantity = DecimalField(required=True)
    unit_price = DecimalField(required=True)  # Price per credit at time of order
    total_price = DecimalField(required=True)
    currency = StringField(default='INR')
    
    # Payment
    payment_method = StringField()  # BANK_TRANSFER, CARD, WALLET, etc.
    payment_reference = StringField()
    payment_date = DateTimeField()
    
    # Status
    status = StringField(
        choices=OrderStatusChoices.CHOICES,
        default=OrderStatusChoices.PENDING_PAYMENT
    )
    
    # Terms & conditions
    terms_accepted = BooleanField(default=False)
    accepted_at = DateTimeField()
    
    # Delivery & completion
    delivery_date = DateTimeField()
    completed_at = DateTimeField()
    
    # Metadata
    metadata = DictField()
    notes = StringField()
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"{self.order_id} - {self.quantity} credits @ {self.total_price} {self.currency}"


class TradeHistory(Document):
    """
    Trade history - records historical trades and market data
    """
    
    meta = {
        'collection': 'trade_histories',
        'indexes': [
            'listing',
            'order',
            'timestamp',
        ],
    }
    
    listing = ReferenceField(Listing, required=True)
    order = ReferenceField(Order, required=True)
    
    # Trade details
    quantity = DecimalField(required=True)
    price_per_credit = DecimalField(required=True)
    total_price = DecimalField(required=True)
    
    # Market data
    market_price_snapshot = DictField()  # Record market conditions at time of trade
    
    timestamp = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"Trade: {self.quantity} credits @ {self.price_per_credit}"
