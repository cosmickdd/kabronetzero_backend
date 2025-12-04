"""
Retirement models - Carbon credit retirement and retirement certificates
"""

from mongoengine import (
    Document, StringField, ReferenceField, DateTimeField, BooleanField,
    DecimalField, DictField
)
from datetime import datetime
import uuid


class RetirementPurposeChoices:
    """Retirement purpose constants"""
    COMPLIANCE = 'COMPLIANCE'
    VOLUNTARY = 'VOLUNTARY'
    ESG_CLAIM = 'ESG_CLAIM'
    CORPORATE_COMMITMENT = 'CORPORATE_COMMITMENT'
    REGULATORY_REQUIREMENT = 'REGULATORY_REQUIREMENT'
    
    CHOICES = [
        (COMPLIANCE, 'Regulatory Compliance'),
        (VOLUNTARY, 'Voluntary Offset'),
        (ESG_CLAIM, 'ESG Claim'),
        (CORPORATE_COMMITMENT, 'Corporate Commitment'),
        (REGULATORY_REQUIREMENT, 'Regulatory Requirement'),
    ]


class RetirementRecord(Document):
    """
    Retirement record - records retirement of carbon credits
    """
    
    meta = {
        'collection': 'retirement_records',
        'indexes': [
            'credit_batch',
            'retired_by_org',
            'reference_id',
            'retirement_date',
            'created_at',
        ],
    }
    
    # Reference ID for public lookups
    reference_id = StringField(required=True, unique=True)  # Public reference number
    
    # Credit source
    credit_batch = ReferenceField('apps.registry.CreditBatch', required=True)
    quantity_retired = DecimalField(required=True)  # Number of credits retired
    
    # Organization & user
    retired_by_org = ReferenceField('apps.organizations.Organization', required=True)
    retired_by_user = ReferenceField('apps.accounts.UserProfile', required=True)
    
    # Purpose & reason
    purpose = StringField(
        choices=RetirementPurposeChoices.CHOICES,
        required=True,
        default=RetirementPurposeChoices.VOLUNTARY
    )
    reason = StringField()  # Detailed reason for retirement
    
    # Retirement details
    retirement_date = DateTimeField(required=True)
    project_name = StringField()  # Project that generated these credits (denormalized)
    carbon_category = StringField()  # Carbon category (denormalized)
    
    # Certificate generation
    certificate_generated = BooleanField(default=False)
    certificate_number = StringField(unique=True)
    certificate_url = StringField()
    
    # Verification
    is_verified = BooleanField(default=False)
    verified_by = ReferenceField('apps.accounts.UserProfile')
    verified_at = DateTimeField()
    
    # Metadata
    metadata = DictField()
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"Retirement: {self.quantity_retired} credits - {self.reference_id}"


class RetirementCertificate(Document):
    """
    Retirement certificate - NFT-like retirement record with public verification
    """
    
    meta = {
        'collection': 'retirement_certificates',
        'indexes': [
            'certificate_number',
            'reference_id',
            'retired_by_org',
            'created_at',
        ],
    }
    
    # Identification
    certificate_number = StringField(required=True, unique=True)
    reference_id = StringField(required=True, unique=True)  # Public reference
    
    # Source
    retirement_record = ReferenceField(RetirementRecord, required=True)
    credit_batch = ReferenceField('apps.registry.CreditBatch', required=True)
    
    # Details
    quantity = DecimalField(required=True)
    retired_by_org = ReferenceField('apps.organizations.Organization', required=True)
    retirement_date = DateTimeField(required=True)
    purpose = StringField(required=True)
    
    # Certificate status
    is_active = BooleanField(default=True)
    is_revoked = BooleanField(default=False)
    revocation_reason = StringField()
    revoked_at = DateTimeField()
    revoked_by = ReferenceField('apps.accounts.UserProfile')
    
    # Public access token
    public_access_token = StringField(unique=True)  # Token for public certificate viewing
    
    # Certificate metadata
    certificate_url = StringField()
    certificate_hash = StringField()  # Blockchain hash if integrated
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"Certificate: {self.certificate_number}"
