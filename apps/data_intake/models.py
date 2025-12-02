"""
Data Intake app models - IoT, Satellite, Manual data ingestion
"""

from mongoengine import (
    Document, StringField, DecimalField, DateTimeField,
    ReferenceField, DictField
)
from projects.models import Project
from datetime import datetime


class DataSourceTypeChoices:
    """Data source type constants"""
    IOT = 'IOT'
    SATELLITE = 'SATELLITE'
    MANUAL = 'MANUAL'

    CHOICES = [
        (IOT, 'IoT Device'),
        (SATELLITE, 'Satellite Data'),
        (MANUAL, 'Manual Entry'),
    ]


class MetricTypeChoices:
    """Metric type constants"""
    CO2_CONCENTRATION = 'CO2_CONCENTRATION'
    ENERGY_CONSUMPTION = 'ENERGY_CONSUMPTION'
    BIOMASS_INDEX = 'BIOMASS_INDEX'
    TEMPERATURE = 'TEMPERATURE'
    RAINFALL = 'RAINFALL'
    SOIL_MOISTURE = 'SOIL_MOISTURE'
    TREE_COUNT = 'TREE_COUNT'
    VEGETATION_INDEX = 'VEGETATION_INDEX'

    CHOICES = [
        (CO2_CONCENTRATION, 'CO2 Concentration'),
        (ENERGY_CONSUMPTION, 'Energy Consumption'),
        (BIOMASS_INDEX, 'Biomass Index'),
        (TEMPERATURE, 'Temperature'),
        (RAINFALL, 'Rainfall'),
        (SOIL_MOISTURE, 'Soil Moisture'),
        (TREE_COUNT, 'Tree Count'),
        (VEGETATION_INDEX, 'Vegetation Index (NDVI)'),
    ]


class DataSource(Document):
    """Data source configuration"""
    
    meta = {
        'collection': 'data_sources',
        'indexes': [
            'project',
            'type',
            'created_at',
        ],
    }
    
    project = ReferenceField(Project, required=True)
    name = StringField(required=True)
    description = StringField()
    
    type = StringField(
        choices=DataSourceTypeChoices.CHOICES,
        required=True
    )
    
    # Source-specific metadata
    metadata = DictField()  # Device ID, API endpoint, satellite provider, etc.
    
    # Status & tracking
    is_active = BooleanField(default=True)
    last_data_received = DateTimeField()
    
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"{self.project.name} - {self.name}"


class DataPoint(Document):
    """Individual data point from a source"""
    
    meta = {
        'collection': 'data_points',
        'indexes': [
            {'fields': ['data_source', 'timestamp']},
            'project',
            'metric_type',
            'timestamp',
            'created_at',
        ],
    }
    
    data_source = ReferenceField(DataSource, required=True)
    project = ReferenceField(Project, required=True)  # Denormalized for query efficiency
    
    metric_type = StringField(
        choices=MetricTypeChoices.CHOICES,
        required=True
    )
    
    # Data
    value = DecimalField(required=True)
    unit = StringField(required=True)  # e.g., 'ppm', 'kWh', 'tons', '%'
    
    # Raw data
    raw_payload = DictField()  # Original data from source
    
    # Quality & validation
    is_validated = BooleanField(default=False)
    validation_status = StringField()  # PASS, FAIL, REQUIRES_REVIEW
    validation_notes = StringField()
    
    # Timestamps
    timestamp = DateTimeField(required=True)  # When data was collected
    created_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"{self.project.name} - {self.metric_type}: {self.value} {self.unit}"


class DataAggregation(Document):
    """Aggregated data for reporting"""
    
    meta = {
        'collection': 'data_aggregations',
        'indexes': [
            'project',
            'metric_type',
            'period',
        ],
    }
    
    project = ReferenceField(Project, required=True)
    metric_type = StringField(required=True)
    
    period = StringField(required=True)  # DAILY, WEEKLY, MONTHLY
    period_start = DateTimeField(required=True)
    period_end = DateTimeField(required=True)
    
    # Aggregated values
    count = StringField()
    sum_value = DecimalField()
    avg_value = DecimalField()
    min_value = DecimalField()
    max_value = DecimalField()
    
    unit = StringField()
    
    created_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"{self.project.name} - {self.metric_type} ({self.period})"
