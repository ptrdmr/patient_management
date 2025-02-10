import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'patient_management.settings')

import django
django.setup()

from django.conf import settings

print("DEBUG =", settings.DEBUG)
print("ALLOWED_HOSTS =", settings.ALLOWED_HOSTS)
print("BASE_DIR =", settings.BASE_DIR)
print("Settings module =", os.environ.get('DJANGO_SETTINGS_MODULE')) 