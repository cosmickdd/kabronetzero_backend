"""
Project models
"""

from mongoengine import Document, StringField, ReferenceField, DateTimeField, ListField
from datetime import datetime


class ProjectStatusChoices:
    """Project status choices"""
    DRAFT = 'draft'
    ACTIVE = 'active'
    COMPLETED = 'completed'
    ARCHIVED = 'archived'
    
    CHOICES = [
        (DRAFT, 'Draft'),
        (ACTIVE, 'Active'),
        (COMPLETED, 'Completed'),
        (ARCHIVED, 'Archived'),
    ]


class CarbonCategoryChoices:
    """Carbon category choices"""
    ENERGY = 'energy'
    AGRICULTURE = 'agriculture'
    WASTE = 'waste'
    FORESTRY = 'forestry'
    
    CHOICES = [
        (ENERGY, 'Energy'),
        (AGRICULTURE, 'Agriculture'),
        (WASTE, 'Waste'),
        (FORESTRY, 'Forestry'),
    ]


class StandardChoices:
    """Standard choices"""
    VCS = 'vcs'
    GOLD = 'gold'
    CAR = 'car'
    
    CHOICES = [
        (VCS, 'VCS'),
        (GOLD, 'Gold Standard'),
        (CAR, 'CAR'),
    ]


class CarbonCategory(Document):
    """Carbon category document"""
    name = StringField(required=True)
    code = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'carbon_categories'
    }


class ProjectMethodology(Document):
    """Project methodology document"""
    name = StringField(required=True)
    standard = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'project_methodologies'
    }


class Project(Document):
    """Project document"""
    name = StringField(required=True)
    organization = ReferenceField('apps.organizations.Organization')
    carbon_category = ReferenceField(CarbonCategory)
    methodology = ReferenceField(ProjectMethodology)
    status = StringField(default=ProjectStatusChoices.DRAFT)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'projects'
    }
