"""
Vercel WSGI entry point for Django application
"""

import os
import sys
import django
from django.core.wsgi import get_wsgi_application

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Setup Django
django.setup()

# Get WSGI application
application = get_wsgi_application()
