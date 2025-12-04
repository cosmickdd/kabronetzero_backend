"""
Vercel serverless handler for Django application
Uses http.server.BaseHTTPRequestHandler interface
"""

import os
import sys
from http.server import BaseHTTPRequestHandler
import django
from django.core.wsgi import get_wsgi_application
from io import BytesIO

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Setup Django
django.setup()

# Get WSGI application
wsgi_app = get_wsgi_application()


class handler(BaseHTTPRequestHandler):
    """
    Vercel serverless handler extending BaseHTTPRequestHandler
    """
    
    def do_GET(self):
        self.route_to_django('GET')
    
    def do_POST(self):
        self.route_to_django('POST')
    
    def do_PUT(self):
        self.route_to_django('PUT')
    
    def do_PATCH(self):
        self.route_to_django('PATCH')
    
    def do_DELETE(self):
        self.route_to_django('DELETE')
    
    def do_HEAD(self):
        self.route_to_django('HEAD')
    
    def do_OPTIONS(self):
        self.route_to_django('OPTIONS')
    
    def route_to_django(self, method):
        """Route request through Django WSGI app"""
        
        # Build environ
        environ = {
            'REQUEST_METHOD': method,
            'SCRIPT_NAME': '',
            'PATH_INFO': self.path.split('?')[0],
            'QUERY_STRING': self.path.split('?')[1] if '?' in self.path else '',
            'CONTENT_TYPE': self.headers.get('content-type', ''),
            'CONTENT_LENGTH': self.headers.get('content-length', ''),
            'SERVER_NAME': self.headers.get('host', 'vercel.app'),
            'SERVER_PORT': '443',
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'https',
            'wsgi.input': BytesIO(),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': True,
            'wsgi.run_once': False,
        }
        
        # Add headers
        for header, value in self.headers.items():
            header_key = 'HTTP_' + header.upper().replace('-', '_')
            environ[header_key] = value
        
        # Response tracking
        response_status = '200 OK'
        response_headers = []
        
        def start_response(status, headers):
            nonlocal response_status, response_headers
            response_status = status
            response_headers = headers
            return lambda data: None
        
        try:
            # Call WSGI app
            app_iter = wsgi_app(environ, start_response)
            
            # Send response
            status_code = int(response_status.split(' ', 1)[0])
            self.send_response(status_code)
            
            for header_name, header_value in response_headers:
                self.send_header(header_name, header_value)
            
            self.end_headers()
            
            # Send body
            for data in app_iter:
                if data:
                    self.wfile.write(data)
                    
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_msg = f'{{"error": "Internal Server Error", "message": "{str(e)}"}}'
            self.wfile.write(error_msg.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass
