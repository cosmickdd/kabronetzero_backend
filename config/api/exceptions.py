"""
Custom exception handlers for DRF
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        response.data = {
            'error': True,
            'message': str(response.data),
            'status_code': response.status_code,
        }
    
    return response
