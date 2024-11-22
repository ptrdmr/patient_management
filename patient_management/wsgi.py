"""
WSGI config for patient_management project.
"""
import os
import sys
from django.core.wsgi import get_wsgi_application

# Add the project directory to the Python path
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(current_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'patient_management.settings')

try:
    application = get_wsgi_application()
except Exception as e:
    print(f"Error loading WSGI application: {e}")
    raise
