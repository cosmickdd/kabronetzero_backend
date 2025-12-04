"""
Django settings for kabro_netzero project.
"""

import os
from pathlib import Path
from datetime import timedelta
from urllib.parse import quote_plus

import environ
from mongoengine import connect, disconnect

# Initialize environment variables
env = environ.Env()
environ.Env.read_env()

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = env('SECRET_KEY', default='django-insecure-changeme')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party
    'rest_framework',
    'corsheaders',
    'django_filters',
    
    # Local apps
    'apps.accounts.apps.AccountsConfig',
    'apps.organizations.apps.OrganizationsConfig',
    'apps.projects.apps.ProjectsConfig',
    'apps.data_intake.apps.DataIntakeConfig',
    'apps.mrv.apps.MrvConfig',
    'apps.registry.apps.RegistryConfig',
    'apps.tokenization.apps.TokenizationConfig',
    'apps.marketplace.apps.MarketplaceConfig',
    'apps.retirement.apps.RetirementConfig',
    'apps.esg.apps.EsgConfig',
    'apps.api.apps.ApiConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'config.middleware.MongoDBConnectionMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database - MongoDB with MongoEngine
MONGODB_URI = env('MONGODB_URI', default='mongodb://localhost:27017/kabro_netzero_db')
MONGODB_DB_NAME = env('MONGODB_DB_NAME', default='kabro_netzero_db')

# For serverless environments, defer MongoDB connection to avoid blocking startup
# Only initialize connection if explicitly requested (e.g., during actual app requests)
def init_mongodb_connection():
    """Initialize MongoDB connection - called lazily to avoid blocking serverless startup"""
    try:
        from mongoengine import get_db, connect, disconnect
        
        try:
            # Check if already connected
            get_db()
            return True  # Already connected
        except:
            pass  # Not connected yet
        
        try:
            disconnect()
        except:
            pass
        
        connect(
            db=MONGODB_DB_NAME,
            host=MONGODB_URI,
            connect=False,
            tz_aware=True,
            serverSelectionTimeoutMS=5000,
        )
        return True
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Could not connect to MongoDB: {e}")
        return False

# In Vercel/serverless, skip startup connection to avoid timeout
# Always defer to first request or explicit call
import sys
is_serverless = 'vercel' in sys.modules or os.environ.get('VERCEL') == '1'

if not is_serverless:
    # Only try to connect at startup if NOT in serverless
    try:
        init_mongodb_connection()
    except Exception as e:
        print(f"Warning: Could not connect to MongoDB at startup: {e}")
        print("The application will attempt to connect on first database access.")

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================
# DJANGO REST FRAMEWORK CONFIGURATION
# ============================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'EXCEPTION_HANDLER': 'apps.api.exceptions.custom_exception_handler',
}

# ============================================
# JWT CONFIGURATION
# ============================================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': env('JWT_SECRET_KEY', default=SECRET_KEY),
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

# ============================================
# CORS CONFIGURATION
# ============================================
CORS_ALLOWED_ORIGINS = env.list(
    'CORS_ALLOWED_ORIGINS',
    default=['http://localhost:3000', 'http://localhost:8000']
)
CORS_ALLOW_CREDENTIALS = True

# ============================================
# LOGGING
# ============================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {name} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'kabro_netzero': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# ============================================
# BLOCKCHAIN SERVICE CONFIGURATION
# ============================================
BLOCKCHAIN_SERVICE_URL = env('BLOCKCHAIN_SERVICE_URL', default='http://localhost:5000')
BLOCKCHAIN_API_KEY = env('BLOCKCHAIN_API_KEY', default='')
BLOCKCHAIN_CHAIN_DEFAULT = env('BLOCKCHAIN_CHAIN_DEFAULT', default='POLYGON')

# ============================================
# CELERY CONFIGURATION
# ============================================
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# ============================================
# CUSTOM SETTINGS
# ============================================
AUTH_USER_MODEL = 'auth.User'  # Using Django's built-in User for auth, MongoEngine for business data
APPEND_SLASH = False
