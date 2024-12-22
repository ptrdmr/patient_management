# Monitoring Guide

## Overview
This document outlines the monitoring and observability setup for the Patient Input Application, focusing on patient data integrity, system performance, and security monitoring.

## Application Metrics

### Patient Data Metrics
```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Patient record metrics
PATIENT_RECORDS = Counter(
    'patient_records_total',
    'Total number of patient records',
    ['record_type']
)

RECORD_CREATION_LATENCY = Histogram(
    'record_creation_seconds',
    'Record creation latency',
    ['record_type']
)

ACTIVE_PATIENTS = Gauge(
    'active_patients_total',
    'Number of active patients'
)

# Clinical data metrics
LAB_RESULTS = Counter(
    'lab_results_total',
    'Total number of lab results',
    ['lab_type']
)

VITALS_RECORDED = Counter(
    'vitals_recorded_total',
    'Total number of vital signs recorded',
    ['vital_type']
)
```

### Performance Monitoring
```python
# monitoring/middleware.py
import time
from prometheus_client import Histogram

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['view_name', 'method']
)

class PerformanceMonitoringMiddleware:
    """Middleware to monitor request performance."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        
        if hasattr(request, 'resolver_match'):
            view_name = request.resolver_match.view_name
            REQUEST_LATENCY.labels(
                view_name=view_name,
                method=request.method
            ).observe(time.time() - start_time)
        
        return response
```

## Error Tracking

### Sentry Configuration
```python
# settings/production.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[
        DjangoIntegration(),
    ],
    traces_sample_rate=1.0,
    send_default_pii=False,
    before_send=lambda event, hint: filter_sensitive_data(event)
)

def filter_sensitive_data(event):
    """Remove sensitive patient data from error reports."""
    if 'extra' in event:
        if 'patient_id' in event['extra']:
            event['extra']['patient_id'] = '[FILTERED]'
    return event
```

## Logging Configuration

### Application Logging
```python
# settings/production.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/patient_input/app.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'security': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/patient_input/security.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'verbose',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'patient_records': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'security': {
            'handlers': ['security'],
            'level': 'INFO',
            'propagate': False,
        }
    }
}
```

### Security Audit Logging
```python
import logging

security_logger = logging.getLogger('security')

def log_security_event(user, event_type, details):
    """Log security-related events."""
    security_logger.info(
        'Security event: %s, User: %s, Details: %s',
        event_type,
        user.username,
        details
    )
```

## Database Monitoring

### Connection Pool Metrics
```python
# monitoring/db.py
from django.db import connection
from prometheus_client import Gauge

DB_CONNECTIONS = Gauge(
    'db_connections_total',
    'Number of database connections',
    ['state']
)

def update_db_metrics():
    """Update database connection metrics."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT state, count(*) 
            FROM pg_stat_activity 
            GROUP BY state
        """)
        for state, count in cursor.fetchall():
            DB_CONNECTIONS.labels(state=state).set(count)
```

### Query Performance
```python
# monitoring/db.py
from django.db import connection
from prometheus_client import Histogram

QUERY_DURATION = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['query_type']
)

class QueryMonitoringMiddleware:
    """Monitor database query performance."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        initial_queries = len(connection.queries)
        
        response = self.get_response(request)
        
        for query in connection.queries[initial_queries:]:
            QUERY_DURATION.labels(
                query_type=self._get_query_type(query['sql'])
            ).observe(float(query['time']))
        
        return response
    
    def _get_query_type(self, sql):
        """Determine query type from SQL."""
        sql = sql.strip().upper()
        if sql.startswith('SELECT'):
            return 'select'
        elif sql.startswith('INSERT'):
            return 'insert'
        elif sql.startswith('UPDATE'):
            return 'update'
        elif sql.startswith('DELETE'):
            return 'delete'
        return 'other'
```

## System Health Checks

### Health Check Endpoints
```python
from django.db import connection
from django.core.cache import cache
from django.http import JsonResponse

def health_check(request):
    """Check system health status."""
    checks = {
        'database': check_database(),
        'cache': check_cache(),
        'storage': check_storage(),
    }
    status = 200 if all(checks.values()) else 503
    return JsonResponse({'status': checks}, status=status)

def check_database():
    """Check database connection."""
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            return True
    except Exception:
        return False

def check_cache():
    """Check cache connection."""
    try:
        cache.set('health_check', 'ok', 10)
        return cache.get('health_check') == 'ok'
    except Exception:
        return False

def check_storage():
    """Check storage availability."""
    try:
        path = settings.MEDIA_ROOT
        return os.access(path, os.W_OK)
    except Exception:
        return False
```

## Alert Configuration

### Alert Rules
```python
# monitoring/alerts.py
from django.core.mail import send_mail
from django.conf import settings

ALERT_RULES = {
    'high_error_rate': {
        'threshold': 0.1,  # 10% error rate
        'period': 300,     # 5 minutes
        'severity': 'critical'
    },
    'slow_response_time': {
        'threshold': 2.0,  # 2 seconds
        'period': 300,
        'severity': 'warning'
    },
    'database_connections': {
        'threshold': 80,   # 80% of max connections
        'period': 60,
        'severity': 'warning'
    }
}

def send_alert(alert_type, details):
    """Send alert notification."""
    subject = f"[{ALERT_RULES[alert_type]['severity']}] {alert_type}"
    send_mail(
        subject=subject,
        message=f"Alert Details: {details}",
        from_email=settings.ALERT_FROM_EMAIL,
        recipient_list=settings.ALERT_RECIPIENTS
    )
```

## Related Documentation
- [[Security Implementation]]
- [[Performance Optimization]]
- [[CI CD Pipeline]]
- [[Deployment Guide]]

## Tags
#monitoring #observability #security #performance