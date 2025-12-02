"""
ESG (Environmental, Social & Governance) Reporting app models
"""

from mongoengine import (
    Document, StringField, DecimalField, DateTimeField,
    ReferenceField, DictField
)
from organizations.models import Organization
from datetime import datetime


class ScopeChoices:
    """GHG Emissions scopes"""
    SCOPE1 = 'SCOPE1'
    SCOPE2 = 'SCOPE2'
    SCOPE3 = 'SCOPE3'

    CHOICES = [
        (SCOPE1, 'Scope 1 (Direct)'),
        (SCOPE2, 'Scope 2 (Indirect - Energy)'),
        (SCOPE3, 'Scope 3 (Indirect - Other)'),
    ]


class ReportTypeChoices:
    """ESG Report types"""
    BRSR = 'BRSR'
    GHG_PROTOCOL = 'GHG_PROTOCOL'
    IFRS_S2 = 'IFRS_S2'
    CUSTOM = 'CUSTOM'

    CHOICES = [
        (BRSR, 'BRSR (India)'),
        (GHG_PROTOCOL, 'GHG Protocol'),
        (IFRS_S2, 'IFRS S2'),
        (CUSTOM, 'Custom Report'),
    ]


class EmissionInventory(Document):
    """Organization's emissions inventory"""
    
    meta = {
        'collection': 'emission_inventories',
        'indexes': [
            'organization',
            'year',
            'scope',
        ],
    }
    
    organization = ReferenceField(Organization, required=True)
    
    # Time period
    year = StringField(required=True)
    
    # Emissions data
    scope = StringField(
        choices=ScopeChoices.CHOICES,
        required=True
    )
    emissions_value = DecimalField(required=True)  # In tons CO2e
    unit = StringField(default='tons CO2e')
    
    # Data source & methodology
    calculation_methodology = StringField()
    data_quality = StringField()  # HIGH, MEDIUM, LOW
    
    # Details by category
    category_breakdown = DictField()  # e.g., {'electricity': 100, 'natural_gas': 50}
    
    # Supporting info
    notes = StringField()
    verified = BooleanField(default=False)
    verified_by = StringField()
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"{self.organization.name} - {self.year} {self.scope}"


class ESGReport(Document):
    """ESG & Sustainability report for an organization"""
    
    meta = {
        'collection': 'esg_reports',
        'indexes': [
            'organization',
            'report_year',
            'report_type',
        ],
    }
    
    organization = ReferenceField(Organization, required=True)
    
    # Report details
    report_type = StringField(
        choices=ReportTypeChoices.CHOICES,
        required=True
    )
    
    report_year = StringField(required=True)
    period_start = DateTimeField()
    period_end = DateTimeField()
    
    # Report content
    title = StringField()
    description = StringField()
    
    # Emissions summary
    total_scope1 = DecimalField()
    total_scope2 = DecimalField()
    total_scope3 = DecimalField()
    total_emissions = DecimalField()
    
    # Credits & offsets
    carbon_credits_retired = DecimalField()
    carbon_credits_purchased = DecimalField()
    net_emissions_after_credits = DecimalField()
    
    # Generation metadata
    generated_by_email = StringField()
    generated_at = DateTimeField()
    
    # Report file
    report_file_url = StringField()
    report_payload = DictField()  # Full report data
    
    # Status
    is_published = BooleanField(default=False)
    published_at = DateTimeField()
    
    # Metadata
    metadata = DictField()
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"ESG Report: {self.organization.name} {self.report_year}"


class ESGGoal(Document):
    """ESG sustainability goals for an organization"""
    
    meta = {
        'collection': 'esg_goals',
        'indexes': [
            'organization',
            'target_year',
        ],
    }
    
    organization = ReferenceField(Organization, required=True)
    
    # Goal details
    title = StringField(required=True)
    description = StringField()
    category = StringField()  # EMISSIONS, RENEWABLE, WATER, WASTE, SOCIAL, GOVERNANCE
    
    # Target
    target_value = DecimalField(required=True)
    target_unit = StringField()  # tons CO2e, %, kWh, etc.
    target_year = StringField()
    baseline_value = DecimalField()
    baseline_year = StringField()
    
    # Progress tracking
    current_value = DecimalField()
    current_value_year = StringField()
    progress_percentage = DecimalField()
    
    # Tracking
    is_active = BooleanField(default=True)
    status = StringField()  # ON_TRACK, AT_RISK, BEHIND, COMPLETED
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"Goal: {self.title} ({self.target_year})"
