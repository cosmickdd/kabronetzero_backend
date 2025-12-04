"""
Registry models - Carbon credit issuance, lifecycle, and serialization
"""

from mongoengine import (
    Document, StringField, IntField, ReferenceField, DateTimeField, DecimalField,
    BooleanField, EmbeddedDocument, EmbeddedDocumentField, ListField, DictField
)
from datetime import datetime
import uuid


class BatchStatusChoices:
    """Batch status constants"""
    ISSUED = 'ISSUED'
    PARTIALLY_RETIRED = 'PARTIALLY_RETIRED'
    FULLY_RETIRED = 'FULLY_RETIRED'
    LOCKED = 'LOCKED'
    ARCHIVED = 'ARCHIVED'
    
    CHOICES = [
        (ISSUED, 'Issued'),
        (PARTIALLY_RETIRED, 'Partially Retired'),
        (FULLY_RETIRED, 'Fully Retired'),
        (LOCKED, 'Locked'),
        (ARCHIVED, 'Archived'),
    ]


class CreditStatusChoices:
    """Credit unit status constants"""
    AVAILABLE = 'AVAILABLE'
    RESERVED = 'RESERVED'
    TRADED = 'TRADED'
    RETIRED = 'RETIRED'
    CANCELLED = 'CANCELLED'
    
    CHOICES = [
        (AVAILABLE, 'Available'),
        (RESERVED, 'Reserved'),
        (TRADED, 'Traded'),
        (RETIRED, 'Retired'),
        (CANCELLED, 'Cancelled'),
    ]


class CreditUnit(EmbeddedDocument):
    """Individual carbon credit unit"""
    serial_number = StringField(required=True, unique=True)  # Unique identifier
    status = StringField(
        choices=CreditStatusChoices.CHOICES,
        default=CreditStatusChoices.AVAILABLE
    )
    owner_organization = ReferenceField('apps.organizations.Organization')
    current_holder = ReferenceField('apps.organizations.Organization')
    
    created_at = DateTimeField(default=datetime.utcnow)
    retired_at = DateTimeField()


class CreditBatch(Document):
    """
    Credit batch - group of carbon credits issued for a project
    """
    
    meta = {
        'collection': 'credit_batches',
        'indexes': [
            'batch_id',
            'project',
            'mrv_request',
            'status',
            'issued_date',
            'organization',
        ],
    }
    
    # Batch identification
    batch_id = StringField(required=True, unique=True)  # KABRO-BATCH-YYYYMMDD-XXXX format
    
    # References
    project = ReferenceField('apps.projects.Project', required=True)
    mrv_request = ReferenceField('apps.mrv.MRVRequest', required=True)
    organization = ReferenceField('apps.organizations.Organization', required=True)  # Issuing organization
    carbon_category = ReferenceField('apps.projects.CarbonCategory', required=True)
    
    # Quantity
    total_credits = DecimalField(required=True)  # Total CO2 tons equivalent
    available_credits = DecimalField(required=True)
    retired_credits = DecimalField(default=0)
    
    # Status
    status = StringField(
        choices=BatchStatusChoices.CHOICES,
        default=BatchStatusChoices.ISSUED
    )
    
    # Issuance details
    issued_date = DateTimeField(required=True)
    issued_by = ReferenceField('apps.accounts.UserProfile', required=True)
    
    # Locking (for regulators)
    is_locked = BooleanField(default=False)
    locked_by = ReferenceField('apps.accounts.UserProfile')
    locked_at = DateTimeField()
    lock_reason = StringField()
    
    # Individual credit units
    credit_units = ListField(EmbeddedDocumentField(CreditUnit))
    
    # Metadata
    metadata = DictField()
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"{self.batch_id} - {self.total_credits} credits"


class CreditTransaction(Document):
    """
    Credit transaction - records transfers, trades, retirements
    """
    
    meta = {
        'collection': 'credit_transactions',
        'indexes': [
            'batch',
            'transaction_type',
            'from_organization',
            'to_organization',
            'timestamp',
        ],
    }
    
    batch = ReferenceField(CreditBatch, required=True)
    transaction_id = StringField(required=True, unique=True)  # UUID
    
    # Transaction details
    transaction_type = StringField(required=True)  # ISSUED, TRANSFERRED, TRADED, RETIRED
    quantity = DecimalField(required=True)
    
    # Parties involved
    from_organization = ReferenceField('apps.organizations.Organization')
    to_organization = ReferenceField('apps.organizations.Organization')
    
    # Transaction metadata
    order_reference = StringField()  # Link to marketplace order if applicable
    retirement_reference = StringField()  # Link to retirement record if applicable
    
    details = DictField()  # Transaction-specific details
    
    # Timestamps
    timestamp = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"{self.transaction_type}: {self.quantity} from {self.batch.batch_id}"


class CreditTransactionLog(Document):
    """Legacy transaction log - kept for backward compatibility"""
    
    meta = {
        'collection': 'credit_transaction_logs',
        'indexes': [
            'batch',
            'timestamp',
        ],
    }
    
    batch = ReferenceField(CreditBatch)
    transaction = ReferenceField(CreditTransaction)
    transaction_id = StringField(required=True, unique=True)
    
    details = DictField()
    
    timestamp = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"TransactionLog: {self.transaction_id}"
