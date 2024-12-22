# Performance Optimization

## Overview
This document outlines performance optimization strategies and best practices for the Patient Management System, ensuring optimal speed and resource utilization.

## Database Optimization

### Query Optimization
```python
# Good: Efficient querying
from django.db.models import Prefetch

def get_patient_with_records(patient_id):
    """Efficiently fetch patient with related records."""
    return Patient.objects.prefetch_related(
        Prefetch(
            'medical_records',
            queryset=MedicalRecord.objects.select_related('doctor')
        ),
        'lab_results'
    ).get(id=patient_id)

# Bad: N+1 query problem
def get_patient_records_inefficient(patient_id):
    """Inefficient way to fetch patient records."""
    patient = Patient.objects.get(id=patient_id)
    records = []
    for record in patient.medical_records.all():  # Causes N+1 queries
        records.append({
            'date': record.date,
            'doctor': record.doctor.name  # Another query for each record
        })
    return records
```

### Database Indexes
```python
# models.py
class Patient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    
    class Meta:
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['date_of_birth']),
        ]

class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateTimeField()
    
    class Meta:
        indexes = [
            models.Index(fields=['patient', '-date']),
        ]
```

## Caching Strategy

### Cache Configuration
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_CLASS': 'redis.connection.BlockingConnectionPool',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
                'timeout': 20,
            }
        }
    }
}
```

### View Caching
```python
from django.views.decorators.cache import cache_page
from django.core.cache import cache

@cache_page(60 * 15)  # Cache for 15 minutes
def patient_list(request):
    """Cached view for patient list."""
    patients = Patient.objects.all()
    return render(request, 'patients/list.html', {'patients': patients})

def get_patient_details(patient_id):
    """Cache patient details with manual control."""
    cache_key = f'patient_details_{patient_id}'
    patient_data = cache.get(cache_key)
    
    if patient_data is None:
        patient_data = Patient.objects.get(id=patient_id)
        cache.set(cache_key, patient_data, timeout=3600)
    
    return patient_data
```

## Code Optimization

### Bulk Operations
```python
# Good: Bulk create
def create_lab_results(patient, results_data):
    """Efficiently create multiple lab results."""
    lab_results = [
        LabResult(
            patient=patient,
            test_type=data['test_type'],
            value=data['value']
        )
        for data in results_data
    ]
    LabResult.objects.bulk_create(lab_results)

# Bad: Individual creates
def create_lab_results_inefficient(patient, results_data):
    """Inefficient way to create multiple lab results."""
    for data in results_data:
        LabResult.objects.create(  # Creates one at a time
            patient=patient,
            test_type=data['test_type'],
            value=data['value']
        )
```

### Memory Management
```python
from django.db.models import QuerySet

def process_large_dataset():
    """Process large dataset efficiently."""
    # Use iterator() for large querysets
    for patient in Patient.objects.iterator():
        process_patient(patient)

def get_filtered_patients(filters):
    """Efficiently filter patients."""
    queryset = Patient.objects.all()
    
    # Apply filters conditionally
    if filters.get('name'):
        queryset = queryset.filter(
            Q(first_name__icontains=filters['name']) |
            Q(last_name__icontains=filters['name'])
        )
    
    if filters.get('date_range'):
        queryset = queryset.filter(
            date_of_birth__range=filters['date_range']
        )
    
    return queryset
```

## Frontend Optimization

### Asset Management
```python
# settings.py
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Compression settings
COMPRESS_ENABLED = True
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.rCSSMinFilter',
]
COMPRESS_JS_FILTERS = ['compressor.filters.jsmin.JSMinFilter']
```

### Template Optimization
```html
{% load cache %}
{% load static %}

{# Cache template fragment #}
{% cache 3600 patient_list %}
    <ul>
    {% for patient in patients %}
        <li>{{ patient.full_name }}</li>
    {% endfor %}
    </ul>
{% endcache %}

{# Efficient static file loading #}
<link rel="stylesheet" href="{% static 'css/style.min.css' %}">
<script defer src="{% static 'js/app.min.js' %}"></script>
```

## API Optimization

### Response Optimization
```python
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

class OptimizedPagination(PageNumberPagination):
    """Optimized pagination for large datasets."""
    page_size = 50
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data
        })

class PatientViewSet(viewsets.ModelViewSet):
    """Optimized patient viewset."""
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    pagination_class = OptimizedPagination
    
    def get_queryset(self):
        """Optimize queryset based on request."""
        queryset = super().get_queryset()
        if self.action == 'list':
            queryset = queryset.only('id', 'first_name', 'last_name')
        return queryset
```

## Background Tasks

### Task Queue Configuration
```python
# settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# tasks.py
from celery import shared_task

@shared_task
def process_lab_results(results_data):
    """Process lab results asynchronously."""
    for result in results_data:
        process_single_result.delay(result)

@shared_task
def generate_patient_report(patient_id):
    """Generate patient report in background."""
    patient = Patient.objects.get(id=patient_id)
    report = create_report(patient)
    send_email.delay(patient.email, report)
```

## Monitoring Performance

### Performance Metrics
```python
from django.db import connection
from time import time

class PerformanceMiddleware:
    """Middleware to track performance metrics."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time()
        
        # Count queries before request
        initial_queries = len(connection.queries)
        
        response = self.get_response(request)
        
        # Calculate metrics
        duration = time() - start_time
        query_count = len(connection.queries) - initial_queries
        
        # Log or store metrics
        logger.info(
            'Request processed',
            extra={
                'duration': duration,
                'query_count': query_count,
                'path': request.path
            }
        )
        
        return response
```

## Related Documentation
- [[Monitoring Guide]]
- [[Database Design]]
- [[API Architecture]]
- [[Deployment Guide]]

## Tags
#performance #optimization #caching #database 