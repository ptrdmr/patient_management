"""Test settings for the patient management application."""

from .base import *
import os

# Use a fixed secret key for testing
SECRET_KEY = 'django-insecure-test-key-do-not-use-in-production-1234567890'

# Use in-memory SQLite database for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test_patient_db',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
        'TEST': {
            'NAME': 'test_patient_db',
        },
    }
}

# Use in-memory cache for testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Disable static file handling during tests
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Configure media files for testing
MEDIA_ROOT = os.path.join(BASE_DIR, 'test_media')
MEDIA_URL = '/media/'

# Static files configuration for tests
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'patient_records/static'),
]

# Create static directory if it doesn't exist
os.makedirs(STATIC_ROOT, exist_ok=True)

# Ensure static files are collected before tests
import django
django.setup()
from django.core.management import call_command
call_command('collectstatic', '--noinput', '--clear')

# Disable debug toolbar during tests
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: False,
}

# Use MD5 password hasher for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Use a faster test runner
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
        'level': 'CRITICAL',
    },
} 