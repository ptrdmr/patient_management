"""
Local development settings for patient_management project.
"""

from .base import *  # noqa
import sys

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-%p2466)5(%m8u#q_r!^1_u9grk_75s233z=$kulw@@v&jwg^s)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.loca.lt']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'patient_management',
        'USER': 'admin',
        'PASSWORD': 'admin',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Override cache settings for local development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Security settings for development
SECURE_SSL_REDIRECT = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Debug toolbar settings
if 'test' not in sys.argv:  # Only install debug toolbar when not running tests
    try:
        import debug_toolbar
        INSTALLED_APPS += ['debug_toolbar']  # noqa
        MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')  # noqa
        INTERNAL_IPS = ['127.0.0.1']
        DEBUG_TOOLBAR_CONFIG = {
            'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
        }
    except ImportError:
        pass 