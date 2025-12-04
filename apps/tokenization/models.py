"""
Tokenization models - Blockchain integration for carbon credit tokenization
"""

from mongoengine import (
    Document, StringField, DateTimeField, ReferenceField, IntField, 
    DictField, DecimalField, BooleanField
)
from datetime import datetime


class TokenizationStatusChoices:
    """Tokenization job status constants"""
    PENDING = 'PENDING'
    PROCESSING = 'PROCESSING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    RETRYING = 'RETRYING'
    CANCELLED = 'CANCELLED'
    
    CHOICES = [
        (PENDING, 'Pending'),
        (PROCESSING, 'Processing'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
        (RETRYING, 'Retrying'),
        (CANCELLED, 'Cancelled'),
    ]


class BlockchainChainChoices:
    """Supported blockchain chains"""
    ETHEREUM = 'ETHEREUM'
    POLYGON = 'POLYGON'
    BINANCE = 'BINANCE'
    HYPERLEDGER = 'HYPERLEDGER'
    OTHER = 'OTHER'
    
    CHOICES = [
        (ETHEREUM, 'Ethereum'),
        (POLYGON, 'Polygon (Matic)'),
        (BINANCE, 'Binance Smart Chain'),
        (HYPERLEDGER, 'Hyperledger Fabric'),
        (OTHER, 'Other'),
    ]


class TokenizationJob(Document):
    """
    Tokenization job - converts carbon credit batch to blockchain tokens (ERC-1155 style)
    """
    
    meta = {
        'collection': 'tokenization_jobs',
        'indexes': [
            'credit_batch',
            'status',
            'chain',
            'created_at',
            'organization',
        ],
    }
    
    # Identification
    job_id = StringField(required=True, unique=True)
    
    # Credit source
    credit_batch = ReferenceField('apps.registry.CreditBatch', required=True)
    project = ReferenceField('apps.projects.Project', required=True)
    organization = ReferenceField('apps.organizations.Organization', required=True)
    
    # Blockchain configuration
    chain = StringField(
        choices=BlockchainChainChoices.CHOICES,
        required=True,
        default='POLYGON'
    )
    contract_address = StringField()  # Smart contract address
    token_standard = StringField(default='ERC-1155')  # ERC-1155, ERC-721, etc.
    
    # Tokenization details
    quantity_to_tokenize = DecimalField(required=True)
    quantity_tokenized = DecimalField(default=0)
    
    # Status & tracking
    status = StringField(
        choices=TokenizationStatusChoices.CHOICES,
        default=TokenizationStatusChoices.PENDING
    )
    
    external_job_id = StringField()  # External service job ID
    external_service_provider = StringField()  # Name of service provider
    
    # Results
    tx_hash = StringField()  # Transaction hash
    token_id = StringField()  # Token ID on blockchain
    token_address = StringField()  # Token contract address
    metadata_uri = StringField()  # URI pointing to token metadata
    
    # Error handling
    error_message = StringField()
    error_details = StringField()
    retry_count = IntField(default=0)
    max_retries = IntField(default=3)
    
    # User & audit
    initiated_by = ReferenceField('apps.accounts.UserProfile', required=True)
    completed_by = ReferenceField('apps.accounts.UserProfile')
    
    # Metadata
    metadata = DictField()
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    started_at = DateTimeField()
    completed_at = DateTimeField()
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"TokenizationJob: {self.job_id} - {self.status}"


class TokenizationEvent(Document):
    """
    Tokenization blockchain event - records on-chain events
    """
    
    meta = {
        'collection': 'tokenization_events',
        'indexes': [
            'tokenization_job',
            'event_type',
            'timestamp',
        ],
    }
    
    tokenization_job = ReferenceField(TokenizationJob, required=True)
    
    # Event identification
    event_type = StringField(required=True)  # MINTED, TRANSFERRED, RETIRED, BURNED, etc.
    event_name = StringField()
    
    # Blockchain details
    tx_hash = StringField(required=True)
    block_number = IntField()
    block_timestamp = DateTimeField()
    log_index = IntField()
    
    # Event participants
    from_address = StringField()
    to_address = StringField()
    
    # Token details
    token_id = StringField()
    amount = DecimalField()
    contract_address = StringField()
    
    # Event metadata
    event_data = DictField()  # Raw event data
    is_confirmed = BooleanField(default=True)
    
    timestamp = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"TokenizationEvent: {self.event_type} - {self.tx_hash}"
