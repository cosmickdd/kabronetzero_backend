"""
Custom middleware for Kabro NetZero
"""

from django.utils.decorators import decorator_from_middleware_with_args


class MongoDBConnectionMiddleware:
    """
    Initialize MongoDB connection on first request in serverless environments.
    This prevents connection timeout errors during function cold start.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.db_initialized = False
    
    def __call__(self, request):
        # Initialize MongoDB connection on first request
        if not self.db_initialized:
            try:
                from config.settings import init_mongodb_connection
                init_mongodb_connection()
                self.db_initialized = True
            except Exception as e:
                # Log but don't block request if connection fails
                # App can still serve non-database endpoints
                print(f"Warning: Error initializing MongoDB in middleware: {e}")
                self.db_initialized = True
        
        try:
            response = self.get_response(request)
        except Exception as e:
            # If database-related error, return 503 Service Unavailable
            if 'mongodb' in str(e).lower() or 'database' in str(e).lower():
                from django.http import JsonResponse
                print(f"Database error on request: {e}")
                return JsonResponse(
                    {'error': 'Database service temporarily unavailable'},
                    status=503
                )
            raise
        
        return response
