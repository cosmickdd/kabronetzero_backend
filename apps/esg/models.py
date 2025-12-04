"""
ESG models - Environmental, Social, Governance reporting
"""

from mongoengine import (
    Document, StringField, IntField, DecimalField, ReferenceField, 
    DateTimeField, BooleanField, DictField, EmbeddedDocument, EmbeddedDocumentField,
    ListField
)
from datetime import datetime


class ScopeChoices:
    """Emission scope constants"""
    SCOPE1 = 'SCOPE1'
    SCOPE2 = 'SCOPE2'
    SCOPE3 = 'SCOPE3'
    
    CHOICES = [
        (SCOPE1, 'Scope 1 - Direct Emissions'),
        (SCOPE2, 'Scope 2 - Indirect Energy'),
        (SCOPE3, 'Scope 3 - Indirect Supply Chain'),
    ]


class ReportTypeChoices:
    """ESG report type constants"""
    BRSR = 'BRSR'
    GHG_PROTOCOL = 'GHG_PROTOCOL'
    IFRS_S2 = 'IFRS_S2'
    CARBON_DISCLOSURE = 'CARBON_DISCLOSURE'
    CUSTOM = 'CUSTOM'
    
    CHOICES = [
        (BRSR, 'BRSR (India)'),
        (GHG_PROTOCOL, 'GHG Protocol'),
        (IFRS_S2, 'IFRS S2'),
        (CARBON_DISCLOSURE, 'Carbon Disclosure Project'),
        (CUSTOM, 'Custom Report'),
    ]


class EmissionSource(EmbeddedDocument):
    """Emission source embedded document"""
    source_name = StringField(required=True)
    scope = StringField(
        choices=ScopeChoices.CHOICES,
        required=True
    )
    emissions_value = DecimalField(required=True)
    unit = StringField(default='tons CO2e')
    percentage = DecimalField()
    data_source = StringField()
    notes = StringField()


class EmissionInventory(Document):
    """
    Emission inventory - tracks organization's emissions by scope and category
    """
    
    meta = {
        'collection': 'emission_inventories',
        'indexes': [
            'organization',
            'year',
            'created_at',
        ],
    }
    
    # Organization & period
    organization = ReferenceField('apps.organizations.Organization', required=True)
    year = IntField(required=True)
    
    # Scope-based emissions
    scope1_emissions = DecimalField(default=0)  # Direct emissions (tons CO2e)
    scope2_emissions = DecimalField(default=0)  # Indirect energy
    scope3_emissions = DecimalField(default=0)  # Indirect supply chain
    
    total_emissions = DecimalField(default=0)  # Total across all scopes
    net_emissions = DecimalField(default=0)  # After carbon offsets
    
    # Breakdown by source
    emission_sources = EmbeddedDocumentField(EmissionSource)
    
    # Baseline & targets
    baseline_emissions = DecimalField()  # Historical baseline for comparison
    reduction_target = DecimalField()  # Target reduction percentage
    actual_reduction = DecimalField()  # Actual reduction achieved
    
    # Status & verification
    is_verified = BooleanField(default=False)
    verified_by = ReferenceField('apps.accounts.UserProfile')
    verified_at = DateTimeField()
    
    # Data quality
    data_quality_score = DecimalField()  # 0-100 score
    completeness_percentage = DecimalField()  # % of data available
    
    # Metadata
    methodology = StringField()  # Calculation methodology used
    metadata = DictField()
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"{self.organization.name} - {self.year} - {self.total_emissions} tons CO2e"


class ESGReport(Document):
    """
    ESG report - comprehensive sustainability and governance report
    """
    
    meta = {
        'collection': 'esg_reports',
        'indexes': [
            'organization',
            'report_type',
            'created_at',
        ],
    }
    
    # Report identification
    report_id = StringField(required=True, unique=True)
    
    # Organization & period
    organization = ReferenceField('apps.organizations.Organization', required=True)
    period_start = DateTimeField(required=True)
    period_end = DateTimeField(required=True)
    
    # Report specification
    report_type = StringField(
        choices=ReportTypeChoices.CHOICES,
        required=True
    )
    report_title = StringField()
    
    # Environmental metrics
    total_emissions = DecimalField()
    emissions_intensity = DecimalField()  # Per unit of activity
    renewable_energy_percentage = DecimalField()
    water_consumption = DecimalField()
    waste_generated = DecimalField()
    biodiversity_impact = StringField()
    
    # Social metrics
    employee_count = IntField()
    employee_satisfaction_score = DecimalField()
    gender_diversity_percentage = DecimalField()
    health_safety_incidents = IntField()
    community_programs = IntField()
    
    # Governance metrics
    board_independence_percentage = DecimalField()
    executive_compensation_ratio = DecimalField()
    ethics_violations = IntField()
    data_privacy_incidents = IntField()
    regulatory_compliance_score = DecimalField()
    
    # Carbon credits & offsets
    carbon_credits_issued = DecimalField()
    carbon_credits_retired = DecimalField()
    carbon_offsets_purchased = DecimalField()
    
    # Report content
    executive_summary = StringField()
    detailed_payload = DictField()  # Full report data
    report_file_url = StringField()  # Link to PDF/document
    
    # Generation & approval
    generated_by = ReferenceField('apps.accounts.UserProfile', required=True)
    approved_by = ReferenceField('apps.accounts.UserProfile')
    approved_at = DateTimeField()
    
    # Verification & publication
    is_verified = BooleanField(default=False)
    is_public = BooleanField(default=False)
    published_at = DateTimeField()
    
    # Metadata & references
    reference_standards = ListField(StringField())  # Standards referenced (GHG Protocol, etc.)
    external_audit_reference = StringField()
    metadata = DictField()
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"ESG Report: {self.organization.name} - {self.period_start.year}"


from mongoengine import ListField
