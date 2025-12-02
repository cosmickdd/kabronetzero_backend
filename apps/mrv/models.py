"""
MRV app models
"""

from mongoengine import Document, StringField, DateTimeField, ReferenceField, ListField, DecimalField, BooleanField, EmbeddedDocument, EmbeddedDocumentField, DictField, FloatField
from datetime import datetime


class MRVStatusChoices:
    PENDING = 'PENDING'
    UNDER_REVIEW = 'UNDER_REVIEW'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    REQUIRES_REVISION = 'REQUIRES_REVISION'
    
    CHOICES = [
        (PENDING, 'Pending'),
        (UNDER_REVIEW, 'Under Review'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (REQUIRES_REVISION, 'Requires Revision'),
    ]


class AssessmentDecisionChoices:
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    CONDITIONAL = 'CONDITIONAL'
    NEEDS_MORE_DATA = 'NEEDS_MORE_DATA'
    
    CHOICES = [
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (CONDITIONAL, 'Conditionally Approved'),
        (NEEDS_MORE_DATA, 'Needs More Data'),
    ]


class Anomaly(EmbeddedDocument):
    """Anomaly detected in MRV data"""
    type = StringField()
    severity = StringField()  # LOW, MEDIUM, HIGH
    description = StringField()
    recommended_action = StringField()
    detected_at = DateTimeField(default=datetime.utcnow)


class MRVRequest(Document):
    """MRV Request submitted by project developer"""
    
    project = ReferenceField('projects.Project', required=True)
    requested_by_email = StringField(required=True)
    
    # Status
    status = StringField(choices=MRVStatusChoices.CHOICES, default='PENDING')
    
    # Reporting period
    reporting_period_start = DateTimeField()
    reporting_period_end = DateTimeField()
    
    # Evidence
    documentation_urls = ListField(StringField())
    evidence_files = ListField(StringField())  # File paths or URLs
    
    # Initial estimate
    initial_estimate_credits = DecimalField(max_digits=20, decimal_places=4)
    
    # Timestamps
    submitted_at = DateTimeField(default=datetime.utcnow)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'mrv_requests',
        'indexes': ['project', 'status', 'submitted_at'],
    }
    
    def __str__(self):
        return f"MRVRequest for {self.project.name} - {self.status}"


class MRVAssessment(Document):
    """MRV Assessment by validator"""
    
    mrv_request = ReferenceField(MRVRequest, required=True)
    project = ReferenceField('projects.Project', required=True)
    
    # Validator info
    validator_email = StringField(required=True)
    validator_organization = StringField()
    
    # Assessment details
    decision = StringField(choices=AssessmentDecisionChoices.CHOICES, required=True)
    recommended_credits = DecimalField(max_digits=20, decimal_places=4)
    
    # Analysis
    risk_score = FloatField()  # 0-100
    anomalies_detected = ListField(EmbeddedDocumentField(Anomaly))
    assessment_notes = StringField()
    
    # Supporting documents
    assessment_report_url = StringField()
    calculation_methodology = StringField()
    
    # Timestamps
    submitted_at = DateTimeField(default=datetime.utcnow)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'mrv_assessments',
        'indexes': ['mrv_request', 'project', 'decision', 'submitted_at'],
    }
    
    def __str__(self):
        return f"Assessment: {self.mrv_request.project.name} - {self.decision}"


class MRVAuditLog(Document):
    """Audit log for MRV operations"""
    
    mrv_request = ReferenceField(MRVRequest)
    mrv_assessment = ReferenceField(MRVAssessment)
    
    action = StringField()  # SUBMITTED, REVIEWED, APPROVED, REJECTED, etc.
    performed_by = StringField()
    performer_role = StringField()
    
    details = DictField()
    
    timestamp = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'mrv_audit_logs',
        'indexes': ['mrv_request', 'timestamp'],
    }
    
    def __str__(self):
        return f"AuditLog: {self.action} by {self.performed_by}"
