"""
Vercel WSGI Handler for Django
This file is used by Vercel to serve the Django application
"""

import os
import sys
import django

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Configure Django
django.setup()

# Import the WSGI application
from config.wsgi import application
