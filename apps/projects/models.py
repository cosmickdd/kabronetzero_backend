"""
Project models - Carbon projects, categories, and methodologies
"""

from mongoengine import (
    Document, StringField, ReferenceField, DateTimeField, ListField,
    EmbeddedDocument, EmbeddedDocumentField, BooleanField, DictField, DecimalField
)
from datetime import datetime


class ProjectStatusChoices:
    """Project status constants"""
    DRAFT = 'DRAFT'
    SUBMITTED_FOR_MRV = 'SUBMITTED_FOR_MRV'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    ACTIVE = 'ACTIVE'
    CLOSED = 'CLOSED'
    ARCHIVED = 'ARCHIVED'
    
    CHOICES = [
        (DRAFT, 'Draft'),
        (SUBMITTED_FOR_MRV, 'Submitted for MRV'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (ACTIVE, 'Active'),
        (CLOSED, 'Closed'),
        (ARCHIVED, 'Archived'),
    ]


class CarbonCategoryChoices:
    """Carbon category constants - Five categories"""
    BLUE = 'BLUE'          # Ocean/aquatic carbon
    GREEN = 'GREEN'        # Forests/vegetation
    BROWN = 'BROWN'        # Soil/agriculture
    GREY = 'GREY'          # Industrial/manufacturing
    BIO = 'BIO'            # Biological/renewable energy
    
    CHOICES = [
        (BLUE, 'Blue Carbon'),
        (GREEN, 'Green Carbon'),
        (BROWN, 'Brown Carbon'),
        (GREY, 'Grey Carbon'),
        (BIO, 'Bio Carbon'),
    ]


class StandardChoices:
    """Carbon credit standard choices"""
    UNFCCC = 'UNFCCC'
    ISO_14064 = 'ISO_14064'
    LOCAL_MOEFCC = 'LOCAL_MOEFCC'
    VCS = 'VCS'
    GOLD = 'GOLD'
    CAR = 'CAR'
    
    CHOICES = [
        (UNFCCC, 'UNFCCC'),
        (ISO_14064, 'ISO 14064'),
        (LOCAL_MOEFCC, 'Local MoEFCC'),
        (VCS, 'VCS'),
        (GOLD, 'Gold Standard'),
        (CAR, 'CAR'),
    ]


class CarbonCategory(Document):
    """
    Carbon category - defines the type of carbon credit
    Five categories: BLUE, GREEN, BROWN, GREY, BIO
    """
    
    meta = {
        'collection': 'carbon_categories',
        'indexes': [
            'code',
        ],
    }
    
    code = StringField(
        choices=CarbonCategoryChoices.CHOICES,
        required=True,
        unique=True
    )
    name = StringField(required=True, max_length=200)
    description = StringField()
    
    # Category-specific metadata
    metadata = DictField()
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class ProjectMethodology(Document):
    """
    Project methodology - defines how emissions are calculated
    """
    
    meta = {
        'collection': 'project_methodologies',
        'indexes': [
            'project',
            'standard',
            'created_at',
        ],
    }
    
    project = ReferenceField('Project', required=True)
    methodology_code = StringField(required=True, max_length=100)  # e.g., "BLUE-MANGROVE-01"
    standard = StringField(
        choices=StandardChoices.CHOICES,
        required=True
    )
    description = StringField()
    
    # Documentation
    documentation_url = StringField()  # Link to methodology document
    documentation_file = StringField()  # Path to uploaded file
    
    # Calculation parameters
    parameters = DictField()  # For storing formulas, conversion factors, etc.
    
    # Status
    is_approved = BooleanField(default=False)
    approved_by = ReferenceField('apps.accounts.UserProfile')
    approved_at = DateTimeField()
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"{self.methodology_code} ({self.standard})"


class ProjectLocation(EmbeddedDocument):
    """Project location embedded document"""
    country = StringField(required=True)
    state = StringField()
    city = StringField()
    latitude = DecimalField()
    longitude = DecimalField()
    address = StringField()
    postal_code = StringField()


class Project(Document):
    """
    Project document - carbon projects implementing reduction measures
    """
    
    meta = {
        'collection': 'projects',
        'indexes': [
            'organization',
            'carbon_category',
            'status',
            'created_at',
            'created_by_email',
        ],
    }
    
    # Basic info
    name = StringField(required=True, max_length=200)
    description = StringField()
    
    # Organization ownership
    organization = ReferenceField('apps.organizations.Organization', required=True)
    created_by_email = StringField()  # Email of user who created project
    
    # Category & methodology
    carbon_category = ReferenceField(CarbonCategory, required=True)
    methodology = ReferenceField(ProjectMethodology)
    
    # Location
    location = EmbeddedDocumentField(ProjectLocation, required=True)
    
    # Baseline and targets
    baseline_emissions = DecimalField(required=True)  # Tons CO2e
    target_reduction = DecimalField()  # Tons CO2e to reduce
    target_reduction_percentage = DecimalField()  # Percentage reduction target
    
    # Status & lifecycle
    status = StringField(
        choices=ProjectStatusChoices.CHOICES,
        default=ProjectStatusChoices.DRAFT
    )
    
    # Dates
    start_date = DateTimeField()
    end_date = DateTimeField()
    submitted_at = DateTimeField()
    approved_at = DateTimeField()
    approved_by = ReferenceField('apps.accounts.UserProfile')
    
    # Verification status
    has_methodology = BooleanField(default=False)
    is_verified = BooleanField(default=False)
    
    # Additional metadata
    project_type = StringField()  # E.g., "Solar Farm", "Afforestation", etc.
    budget = DecimalField()
    tags = ListField(StringField())
    external_id = StringField()  # For integration with external systems
    metadata = DictField()
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"{self.name} ({self.carbon_category.code if self.carbon_category else 'N/A'})"
