"""
Project models
"""

from mongoengine import Document, StringField, ReferenceField, DateTimeField, ListField
from datetime import datetime


class CarbonCategory(Document):
    """Carbon category document"""
    name = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'carbon_categories'
    }


class ProjectMethodology(Document):
    """Project methodology document"""
    name = StringField(required=True)
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
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'projects'
    }
