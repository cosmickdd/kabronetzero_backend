"""
Complete URL Configuration for Kabro NetZero
api/urls.py - Main API routing
"""

from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import os
import logging

logger = logging.getLogger(__name__)

# Health check endpoint (required for Cloud Run)
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Simple health check endpoint - no DB access"""
    try:
        return JsonResponse({
            'status': 'healthy',
            'service': 'kabro-netzero-api',
            'timestamp': str(__import__('datetime').datetime.utcnow())
        })
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Health check failed'
        }, status=500)

# Debug endpoint to check MongoDB connection status
@api_view(['GET'])
@permission_classes([AllowAny])
def db_status(request):
    """Check if MongoDB is configured and accessible - no authentication required"""
    try:
        mongodb_uri = os.environ.get('MONGODB_URI', None)
        
        if not mongodb_uri:
            return JsonResponse({
                'status': 'error',
                'message': 'MONGODB_URI environment variable not set on Vercel',
                'instructions': 'Set MONGODB_URI in Vercel Project Settings → Environment Variables',
                'configured': False
            }, status=503)
        
        # Hide credentials in response
        uri_display = mongodb_uri.replace(mongodb_uri.split('@')[0] if '@' in mongodb_uri else '', 'mongodb://***:***') if '@' in mongodb_uri else mongodb_uri
        
        # Try to connect
        try:
            from mongoengine import connect, disconnect
            try:
                disconnect()
            except:
                pass
            
            connect(
                host=mongodb_uri,
                connect=False,
                serverSelectionTimeoutMS=3000,
            )
            
            return JsonResponse({
                'status': 'connected',
                'message': 'MongoDB connection successful',
                'configured': True,
                'uri_display': uri_display
            })
        except Exception as e:
            error_msg = str(e)
            logger.error(f"MongoDB connection error: {error_msg}")
            
            return JsonResponse({
                'status': 'error',
                'message': f'MongoDB connection failed',
                'configured': True,
                'uri_display': uri_display,
                'error_type': type(e).__name__,
                'error_details': error_msg[:200]  # Truncate for security
            }, status=503)
    except Exception as e:
        logger.error(f"Unexpected error in db_status: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Unexpected error checking database status',
            'error': str(e)[:100]
        }, status=500)

urlpatterns = [
    # Health check (no auth required)
    path('health/', health_check, name='health_check'),
    
    # Database status check (diagnostic, no auth required)
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

