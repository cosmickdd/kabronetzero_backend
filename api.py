"""
Vercel WSGI Handler for Django
This file is used by Vercel to serve the Django application
"""

import os
import sys
import django
from urllib.parse import quote_plus

# Add the project root to the Python path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Handle MongoDB URI escaping for Vercel
# If MONGODB_URI is set, ensure credentials are properly escaped
if 'MONGODB_URI' in os.environ:
    uri = os.environ['MONGODB_URI']
    if uri.startswith(('mongodb://', 'mongodb+srv://')):
        try:
            # Split the URI into parts
            if '@' in uri:
                scheme_and_creds = uri.split('@')[0]  # mongodb+srv://user:pass
                host_part = uri.split('@')[1]  # host and query params
                
                # Extract the scheme
                if '://' in scheme_and_creds:
                    scheme = scheme_and_creds.split('://')[0] + '://'
                    creds = scheme_and_creds.split('://')[1]
                    
                    if ':' in creds:
                        username, password = creds.split(':', 1)
                        # Always re-escape to ensure proper encoding
                        escaped_username = quote_plus(username)
                        escaped_password = quote_plus(password)
                        # Reconstruct URI
                        os.environ['MONGODB_URI'] = f'{scheme}{escaped_username}:{escaped_password}@{host_part}'
        except Exception as e:
            print(f"Warning: Could not auto-escape MongoDB URI: {e}")

# Don't call django.setup() here - config.wsgi.get_wsgi_application() does it
# Import the WSGI application (which calls django.setup internally)
from config.wsgi import application

# Export as 'app' for Vercel WSGI compatibility
# Vercel's Python runtime will use this as the WSGI application
app = application
