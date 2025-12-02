"""
Complete URL Configuration for Kabro NetZero
api/urls.py - Main API routing
"""

from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
import os

# Health check endpoint (required for Cloud Run)
def health_check(request):
    return JsonResponse({'status': 'healthy', 'service': 'kabro-netzero-api'})

# Debug endpoint to check MongoDB connection status
def db_status(request):
    """Check if MongoDB is configured and accessible"""
    mongodb_uri = os.environ.get('MONGODB_URI', 'Not configured')
    
    if mongodb_uri == 'Not configured':
        return JsonResponse({
            'status': 'error',
            'message': 'MONGODB_URI environment variable not set on Vercel',
            'instructions': 'Set MONGODB_URI in Vercel Project Settings → Environment Variables'
        }, status=503)
    
    # Try to connect
    try:
        from mongoengine import connect, disconnect
        disconnect()
        connect(
            host=mongodb_uri,
            connect=False,
            serverSelectionTimeoutMS=5000,
        )
        return JsonResponse({
            'status': 'connected',
            'message': 'MongoDB connection successful'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'MongoDB connection failed: {str(e)}',
            'mongodb_uri_prefix': mongodb_uri.split('@')[-1] if '@' in mongodb_uri else 'no-creds'
        }, status=503)

urlpatterns = [
    # Health check (no auth required, used by Cloud Run)
    path('health/', health_check, name='health_check'),
    
    # Database status check (diagnostic)
    path('db-status/', db_status, name='db_status'),
    
    # JWT Authentication
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API v1 namespace
    path('v1/', include([
        # Auth endpoints
        path('auth/register/', include('apps.accounts.urls')),
        path('auth/login/', include('apps.accounts.urls')),
        
        # Users
        path('users/', include('apps.accounts.urls')),
        
        # Organizations
        path('organizations/', include('apps.organizations.urls')),
        
        # Projects
        path('projects/', include('apps.projects.urls')),
        path('carbon-categories/', include('apps.projects.urls')),
        
        # Data Intake
        path('data-sources/', include('apps.data_intake.urls')),
        path('data-points/', include('apps.data_intake.urls')),
        
        # MRV
        path('mrv/', include('apps.mrv.urls')),
        
        # Registry
        path('registry/', include('apps.registry.urls')),
        
        # Tokenization
        path('tokenization/', include('apps.tokenization.urls')),
        
        # Marketplace
        path('marketplace/', include('apps.marketplace.urls')),
        
        # Retirement
        path('retirement/', include('apps.retirement.urls')),
        
        # ESG
        path('esg/', include('apps.esg.urls')),
    ])),
]
