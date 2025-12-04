"""
Custom middleware for Kabro NetZero
"""

import logging

logger = logging.getLogger(__name__)


class MongoDBConnectionMiddleware:
    """
    Initialize MongoDB connection on first request in serverless environments.
    This prevents connection timeout errors during function cold start.
    
    Designed to be non-blocking - failures don't crash the request.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.db_initialized = False
        self.init_attempted = False
    
    def __call__(self, request):
        # Try to initialize MongoDB connection once per instance
        # But never block requests if it fails
        if not self.init_attempted:
            self.init_attempted = True
            try:
                from config.settings import init_mongodb_connection
                init_mongodb_connection()
                self.db_initialized = True
                logger.info("MongoDB connection initialized successfully")
            except ImportError as e:
                logger.warning(f"Could not import init_mongodb_connection: {e}")
            except Exception as e:
                logger.warning(f"MongoDB initialization failed (non-blocking): {e}")
        
        # Always attempt to get response, even if DB init failed
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            # Log database errors but don't crash
            error_str = str(e).lower()
            if any(term in error_str for term in ['mongodb', 'database', 'connection', 'timeout']):
                logger.error(f"Database error on request to {request.path}: {e}")
                from django.http import JsonResponse
                return JsonResponse(
                    {
                        'error': 'Database service temporarily unavailable',
                        'detail': 'MongoDB connection failed. Please check configuration.'
                    },
                    status=503
                )
            # Re-raise non-database errors
            raise
