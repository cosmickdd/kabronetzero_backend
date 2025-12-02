"""
ESG models
"""

from mongoengine import Document, StringField, IntField, FloatField, ReferenceField, DateTimeField, BooleanField
from datetime import datetime


class EmissionInventory(Document):
    """Emission inventory document"""
    organization = ReferenceField('apps.organizations.Organization')
    project = ReferenceField('apps.projects.Project')
    report_year = IntField()
    scope_1_emissions = FloatField()
    scope_2_emissions = FloatField()
    scope_3_emissions = FloatField()
    net_emissions = FloatField()
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'emission_inventories'
    }


class ESGReport(Document):
    """ESG report document"""
    organization = ReferenceField('apps.organizations.Organization')
    emission_inventory = ReferenceField(EmissionInventory)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'esg_reports'
    }
