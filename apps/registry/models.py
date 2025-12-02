"""
Registry models
"""

from mongoengine import Document, StringField, IntField, ReferenceField, DateTimeField
from datetime import datetime


class CreditBatch(Document):
    """Credit batch document"""
    batch_id = StringField(required=True, unique=True)
    project = ReferenceField('apps.projects.Project')
    total_credits = IntField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'credit_batches'
    }


class CreditTransactionLog(Document):
    """Credit transaction log document"""
    batch = ReferenceField(CreditBatch)
    transaction_id = StringField(required=True, unique=True)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'credit_transaction_logs'
    }


class BatchStatusChoices:
    """Batch status choices"""
    DRAFT = 'draft'
    PENDING = 'pending'
    APPROVED = 'approved'


class CreditStatusChoices:
    """Credit status choices"""
    ACTIVE = 'active'
    RETIRED = 'retired'
