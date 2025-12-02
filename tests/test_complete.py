"""
Unit tests for Kabro NetZero
"""

import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status


class UserAuthenticationTests(TestCase):
    """Test user authentication flows"""
    
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
        }
    
    def test_user_registration(self):
        """Test user registration"""
        response = self.client.post('/api/v1/auth/register/', self.user_data)
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_user_login(self):
        """Test user login"""
        # First register
        self.client.post('/api/v1/auth/register/', self.user_data)
        
        # Then login
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password'],
        }
        response = self.client.post('/api/v1/auth/login/', login_data)
        assert response.status_code == status.HTTP_200_OK


class ProjectManagementTests(TestCase):
    """Test project creation and management"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_project(self):
        """Test project creation"""
        project_data = {
            'name': 'Test Carbon Project',
            'description': 'A test project',
            'carbon_category_id': '1',
            'organization_id': '1',
        }
        response = self.client.post('/api/v1/projects/projects/', project_data)
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_list_projects(self):
        """Test project listing"""
        response = self.client.get('/api/v1/projects/projects/')
        assert response.status_code == status.HTTP_200_OK


class MRVWorkflowTests(TestCase):
    """Test MRV request and assessment flows"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='validator@example.com',
            email='validator@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_mrv_request(self):
        """Test MRV request creation"""
        mrv_data = {
            'project_id': '1',
            'reporting_period_start': '2024-01-01T00:00:00Z',
            'reporting_period_end': '2024-12-31T23:59:59Z',
        }
        response = self.client.post('/api/v1/mrv/requests/', mrv_data)
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_create_assessment(self):
        """Test MRV assessment creation"""
        assessment_data = {
            'mrv_request_id': '1',
            'validator_email': 'validator@example.com',
            'decision': 'APPROVE',
            'recommended_credits': '1000',
        }
        response = self.client.post('/api/v1/mrv/assessments/', assessment_data)
        assert response.status_code == status.HTTP_201_CREATED


class MarketplaceTests(TestCase):
    """Test marketplace listing and order flows"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='buyer@example.com',
            email='buyer@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_listing(self):
        """Test marketplace listing creation"""
        listing_data = {
            'credit_batch_id': '1',
            'seller_organization_id': '1',
            'quantity_available': '1000',
            'unit_price': '10.00',
        }
        response = self.client.post('/api/v1/marketplace/listings/', listing_data)
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_create_order(self):
        """Test order creation"""
        order_data = {
            'listing_id': '1',
            'buyer_organization_id': '2',
            'quantity': '100',
        }
        response = self.client.post('/api/v1/marketplace/orders/', order_data)
        assert response.status_code == status.HTTP_201_CREATED


class RetirementTests(TestCase):
    """Test credit retirement flows"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='buyer@example.com',
            email='buyer@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_retire_credits(self):
        """Test credit retirement"""
        retirement_data = {
            'credit_batch_id': '1',
            'quantity_retired': '100',
            'retired_by_org_id': '1',
            'retirement_date': '2024-01-01T00:00:00Z',
            'purpose': 'VOLUNTARY',
        }
        response = self.client.post('/api/v1/retirement/records/', retirement_data)
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_public_certificate_access(self):
        """Test public retirement certificate access"""
        response = self.client.get('/api/v1/retirement/records/public_certificate/?reference_id=CERT-001')
        assert response.status_code == status.HTTP_200_OK


class ESGReportingTests(TestCase):
    """Test ESG reporting functionality"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='admin@example.com',
            email='admin@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_emission_inventory(self):
        """Test emission inventory creation"""
        inventory_data = {
            'organization_id': '1',
            'year': '2024',
            'scope': 'SCOPE1',
            'emissions_value': '5000',
        }
        response = self.client.post('/api/v1/esg/inventory/', inventory_data)
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_generate_esg_report(self):
        """Test ESG report generation"""
        report_data = {
            'organization_id': '1',
            'report_year': '2024',
        }
        response = self.client.post('/api/v1/esg/reports/generate_report/', report_data)
        assert response.status_code == status.HTTP_201_CREATED
