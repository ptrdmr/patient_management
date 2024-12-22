# Common Issues & Solutions

## Overview
This guide provides solutions to common issues encountered in the Patient Management System, including development, deployment, and runtime problems.

## Development Issues

### Database Migration Issues

#### Issue: Migration Conflicts
```
django.db.migrations.exceptions.InconsistentMigrationHistory
```

**Solution:**
1. Reset migrations:
   ```bash
   python manage.py migrate patient_records zero
   python manage.py migrate patient_records
   ```
2. If problem persists:
   ```bash
   # Remove migration files
   rm */migrations/0*.py
   
   # Recreate migrations
   python manage.py makemigrations
   python manage.py migrate
   ```

#### Issue: Data Loss Prevention
Before any migration:
```bash
# Backup database
pg_dump patient_input_db > backup.sql

# If migration fails
psql patient_input_db < backup.sql
```

### Environment Setup

#### Issue: Virtual Environment Problems
```
Error: No module named 'virtualenv'
```

**Solution:**
```bash
# Install virtualenv
pip install virtualenv

# Create new environment
python -m venv venv

# Activate environment
# Windows
venv\Scripts\activate
# Unix/macOS
source venv/bin/activate
```

#### Issue: Package Conflicts
```
ERROR: pip's dependency resolver could not resolve dependencies
```

**Solution:**
```bash
# Clear pip cache
pip cache purge

# Update pip
python -m pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v
```

## Runtime Issues

### Performance Problems

#### Issue: Slow Database Queries
```python
# Identify slow queries
from django.db import connection

def debug_queries():
    for query in connection.queries:
        if float(query['time']) > 0.5:  # Queries taking > 0.5s
            print(f"Slow query: {query['sql']}")
            print(f"Time: {query['time']}s")
```

**Solution:**
```python
# Add database indexes
class Patient(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['patient_id']),
            models.Index(fields=['last_name', 'first_name']),
        ]

# Use select_related for foreign keys
patients = Patient.objects.select_related('provider').all()

# Use prefetch_related for many-to-many
patients = Patient.objects.prefetch_related('medications').all()
```

#### Issue: Memory Leaks
```python
# Memory usage monitoring
import psutil
import os

def monitor_memory():
    process = psutil.Process(os.getpid())
    print(f"Memory usage: {process.memory_info().rss / 1024 / 1024} MB")
```

**Solution:**
```python
# Implement pagination
from django.core.paginator import Paginator

def get_patient_list(request):
    patient_list = Patient.objects.all()
    paginator = Paginator(patient_list, 25)
    page = request.GET.get('page')
    patients = paginator.get_page(page)
    return patients
```

### Authentication Issues

#### Issue: Session Expiry
```
User unexpectedly logged out
```

**Solution:**
```python
# settings.py
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Middleware for session refresh
class SessionRefreshMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            request.session.modified = True
        return self.get_response(request)
```

#### Issue: CSRF Token Errors
```
CSRF verification failed. Request aborted.
```

**Solution:**
```python
# Template
{% csrf_token %}

# AJAX requests
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

fetch('/api/endpoint/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
});
```

## Deployment Issues

### Server Configuration

#### Issue: Static Files Not Serving
```
404 for static files in production
```

**Solution:**
```python
# settings.py
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Collect static files
python manage.py collectstatic

# Nginx configuration
location /static/ {
    alias /path/to/staticfiles/;
    expires 30d;
    add_header Cache-Control "public, no-transform";
}
```

#### Issue: Database Connection Errors
```
OperationalError: could not connect to server
```

**Solution:**
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 5,
            'retries': 3
        }
    }
}
```

## Security Issues

### Data Protection

#### Issue: Sensitive Data Exposure
```
PHI data visible in logs or error messages
```

**Solution:**
```python
# Custom error handler
class PHIProtectedError(Exception):
    def __str__(self):
        return "Error occurred processing protected health information"

# Logging configuration
LOGGING = {
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'app.log',
            'formatter': 'simple',
            'filters': ['phi_filter']
        }
    },
    'filters': {
        'phi_filter': {
            '()': 'patient_records.logging.PHIFilter'
        }
    }
}
```

#### Issue: SQL Injection Prevention
```python
# Use query parameters
from django.db import connection

def unsafe_query(patient_id):
    # DON'T DO THIS
    cursor.execute(f"SELECT * FROM patients WHERE id = {patient_id}")

def safe_query(patient_id):
    # DO THIS
    cursor.execute("SELECT * FROM patients WHERE id = %s", [patient_id])
```

## Related Documentation
- [[Development Guide]]
- [[Security Implementation]]
- [[Performance Optimization]]
- [[Deployment Guide]]

## Tags
#troubleshooting #issues #solutions #debugging 