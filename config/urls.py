"""
Complete URL Configuration for Kabro NetZero
api/urls.py - Main API routing
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Import ViewSets from respective apps
# In a real project, these would be spread across app-specific urls.py files

urlpatterns = [
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
