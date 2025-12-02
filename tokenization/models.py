"""
Tokenization app models
"""

from mongoengine import Document, StringField, DateTimeField, ReferenceField, IntField, DictField
from datetime import datetime


class TokenizationStatusChoices:
    PENDING = 'PENDING'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    RETRYING = 'RETRYING'
    
    CHOICES = [
        (PENDING, 'Pending'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
        (RETRYING, 'Retrying'),
    ]


class BlockchainChainChoices:
    ETHEREUM = 'ETHEREUM'
    POLYGON = 'POLYGON'
    BINANCE = 'BINANCE'
    HYPERLEDGER = 'HYPERLEDGER'
    
    CHOICES = [
        (ETHEREUM, 'Ethereum'),
        (POLYGON, 'Polygon'),
        (BINANCE, 'Binance Smart Chain'),
        (HYPERLEDGER, 'Hyperledger'),
    ]


class TokenizationJob(Document):
    """Blockchain tokenization job for credit batch"""
    
    credit_batch = ReferenceField('registry.CreditBatch', required=True)
    project = ReferenceField('projects.Project', required=True)
    
    # Blockchain details
    chain = StringField(choices=BlockchainChainChoices.CHOICES, required=True, default='POLYGON')
    contract_address = StringField()
    
    # Status
    status = StringField(choices=TokenizationStatusChoices.CHOICES, default='PENDING')
    external_job_id = StringField()  # External service job ID
    
    # Results
    tx_hash = StringField()  # Transaction hash
    token_id = StringField()  # Token ID on blockchain
    token_address = StringField()  # ERC-1155/ERC-721 address
    
    # Error handling
    error_message = StringField()
    retry_count = IntField(default=0)
    
    # Metadata
    metadata = DictField()
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    started_at = DateTimeField()
    completed_at = DateTimeField()
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'tokenization_jobs',
        'indexes': ['credit_batch', 'status', 'chain'],
    }
    
    def __str__(self):
        return f"TokenizationJob: {self.credit_batch.batch_id} - {self.status}"


class TokenizationEvent(Document):
    """Blockchain tokenization event"""
    
    tokenization_job = ReferenceField(TokenizationJob, required=True)
    
    event_type = StringField()  # MINTED, TRANSFERRED, RETIRED, etc.
    event_name = StringField()
    
    # Blockchain details
    tx_hash = StringField()
    block_number = IntField()
    log_index = IntField()
    
    # Event data
    from_address = StringField()
    to_address = StringField()
    token_id = StringField()
    amount = StringField()
    
    # Metadata
    event_data = DictField()
    
    timestamp = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'tokenization_events',
        'indexes': ['tokenization_job', 'event_type', 'timestamp'],
    }
    
    def __str__(self):
        return f"TokenizationEvent: {self.event_type} - {self.tx_hash}"
