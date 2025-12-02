"""
Vercel WSGI Handler for Django
This file is used by Vercel to serve the Django application
"""

import os
import sys
import django
from urllib.parse import quote_plus

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Handle MongoDB URI escaping for Vercel
# If MONGODB_URI is set but not properly escaped, escape it
if 'MONGODB_URI' in os.environ and os.environ['MONGODB_URI'].startswith('mongodb+srv://'):
    uri = os.environ['MONGODB_URI']
    # Check if credentials need escaping (contains @ in password portion)
    if '@' in uri and uri.count('@') == 1:  # Only one @ means credentials part
        try:
            # Split the URI into parts
            if 'mongodb+srv://' in uri:
                scheme_and_creds = uri.split('@')[0]  # mongodb+srv://user:pass
                host_part = uri.split('@')[1]  # host and query params
                
                # Extract credentials
                creds = scheme_and_creds.replace('mongodb+srv://', '')
                if ':' in creds:
                    username, password = creds.split(':', 1)
                    # Escape both username and password
                    escaped_username = quote_plus(username)
                    escaped_password = quote_plus(password)
                    # Reconstruct URI
                    os.environ['MONGODB_URI'] = f'mongodb+srv://{escaped_username}:{escaped_password}@{host_part}'
        except Exception as e:
            print(f"Warning: Could not auto-escape MongoDB URI: {e}")

# Don't call django.setup() here - config.wsgi.get_wsgi_application() does it
# Import the WSGI application (which calls django.setup internally)
from config.wsgi import application
