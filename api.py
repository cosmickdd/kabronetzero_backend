"""
Vercel serverless handler for Django application
"""

import os
import sys
from io import StringIO
import django
from django.core.wsgi import get_wsgi_application

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Setup Django
django.setup()

# Get WSGI application
wsgi_app = get_wsgi_application()


def handler(request, context):
    """
    Vercel serverless handler
    Converts incoming request to WSGI environ and routes to Django
    """
    # Build the environ dict from Vercel request
    environ = {
        'REQUEST_METHOD': request['httpMethod'],
        'SCRIPT_NAME': '',
        'PATH_INFO': request['path'],
        'QUERY_STRING': request.get('queryStringParameters', '') or '',
        'CONTENT_TYPE': request['headers'].get('content-type', ''),
        'CONTENT_LENGTH': request['headers'].get('content-length', ''),
        'SERVER_NAME': request['headers'].get('host', 'vercel.app'),
        'SERVER_PORT': '443',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': StringIO(request.get('body', '') or ''),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
    }
    
    # Add all headers to environ
    for header, value in request['headers'].items():
        header_key = 'HTTP_' + header.upper().replace('-', '_')
        environ[header_key] = value
    
    # Call the WSGI app
    response_started = False
    response_status = '200 OK'
    response_headers = []
    
    def start_response(status, headers):
        nonlocal response_started, response_status, response_headers
        response_started = True
        response_status = status
        response_headers = headers
        return lambda data: None  # write() function (deprecated but required)
    
    try:
        response_data = wsgi_app(environ, start_response)
        body = b''.join(response_data)
        
        # Parse status code
        status_code = int(response_status.split(' ', 1)[0])
        
        # Convert headers list to dict
        headers_dict = {}
        for header_name, header_value in response_headers:
            headers_dict[header_name] = header_value
        
        return {
            'statusCode': status_code,
            'headers': headers_dict,
            'body': body.decode('utf-8') if isinstance(body, bytes) else body,
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': f'{{"error": "Internal Server Error", "message": "{str(e)}"}}',
            'isBase64Encoded': False
        }
