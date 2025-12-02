"""
Retirement models
"""

from mongoengine import Document, StringField, ReferenceField, DateTimeField, BooleanField
from datetime import datetime


class RetirementPurposeChoices:
    """Retirement purpose choices"""
    ENVIRONMENTAL_IMPACT = 'environmental_impact'
    CORPORATE_COMMITMENT = 'corporate_commitment'
    REGULATORY_COMPLIANCE = 'regulatory_compliance'
    VOLUNTARY_OFFSET = 'voluntary_offset'
    
    CHOICES = [
        (ENVIRONMENTAL_IMPACT, 'Environmental Impact'),
        (CORPORATE_COMMITMENT, 'Corporate Commitment'),
        (REGULATORY_COMPLIANCE, 'Regulatory Compliance'),
        (VOLUNTARY_OFFSET, 'Voluntary Offset'),
    ]


class RetirementRecord(Document):
    """Retirement record document"""
    credit_batch = ReferenceField('apps.registry.CreditBatch')
    retiree_organization = ReferenceField('apps.organizations.Organization')
    quantity_retired = StringField()
    purpose = StringField(default=RetirementPurposeChoices.VOLUNTARY_OFFSET)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'retirement_records'
    }


class RetirementCertificate(Document):
    """Retirement certificate document"""
    retirement_record = ReferenceField(RetirementRecord)
    certificate_number = StringField(unique=True)
    is_verified = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'retirement_certificates'
    }
