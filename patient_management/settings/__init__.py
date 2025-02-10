"""
Settings package initialization.
Handles environment detection and settings module routing.
"""

import os
import sys
from pathlib import Path

# Get the environment setting
DJANGO_ENV = os.environ.get('DJANGO_ENV', 'local').lower()

# Validate the environment
valid_environments = {'local', 'production', 'staging'}
if DJANGO_ENV not in valid_environments:
    print(f"Warning: Invalid DJANGO_ENV '{DJANGO_ENV}'. Defaulting to 'local'")
    DJANGO_ENV = 'local'

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# Import appropriate settings module
if DJANGO_ENV == 'production':
    print("Loading production settings...")
    from .production import *  # noqa
elif DJANGO_ENV == 'staging':
    print("Loading staging settings...")
    from .staging import *  # noqa
else:
    print("Loading local development settings...")
    from .local import *  # noqa

# Print debug information
print(f"Settings loaded from: {__file__}")
print(f"Environment: {DJANGO_ENV}")
print(f"Debug mode: {DEBUG}")  # noqa 