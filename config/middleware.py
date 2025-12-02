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
                print(f"Error initializing MongoDB in middleware: {e}")
                # Don't block request even if connection fails
                self.db_initialized = True
        
        response = self.get_response(request)
        return response
