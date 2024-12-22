# Technical Architecture

## Overview
This document outlines the technical architecture of the Patient Management System, including system components, data flow, and technology stack.

## System Architecture

### High-Level Architecture
```
[Client Browser] ←→ [Web Server (Nginx)]
       ↓
[Django Application Server]
       ↓
[PostgreSQL Database] ←→ [Redis Cache]
```

## Technology Stack

### Backend
- **Framework**: Django 5.1
- **Language**: Python 3.8+
- **Database**: PostgreSQL 13+
- **Cache**: Redis 6+
- **Web Server**: Nginx
- **WSGI Server**: Gunicorn

### Frontend
- **Template Engine**: Django Templates
- **CSS Framework**: Bootstrap 5
- **JavaScript**: Vanilla JS + jQuery
- **AJAX**: Fetch API

### Development Tools
- **Version Control**: Git
- **CI/CD**: GitHub Actions
- **Code Quality**: Black, Flake8, isort
- **Testing**: pytest, coverage.py

## Component Architecture

### Core Components

#### Patient Records Module
```python
patient_records/
├── models/
│   ├── patient.py
│   ├── vitals.py
│   └── labs.py
├── views/
│   ├── patient_views.py
│   └── clinical_views.py
└── services/
    ├── patient_service.py
    └── lab_service.py
```

#### Authentication Module
```python
accounts/
├── models/
│   └── user.py
├── views/
│   └── auth_views.py
└── services/
    └── auth_service.py
```

## Data Architecture

### Database Schema
```sql
-- Core Tables
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    patient_number VARCHAR(20) UNIQUE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    date_of_birth DATE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE vitals (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id),
    blood_pressure VARCHAR(20),
    temperature DECIMAL(4,1),
    recorded_at TIMESTAMP
);
```

### Caching Strategy
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'TIMEOUT': 300,  # 5 minutes
    }
}
```

## Security Architecture

### Authentication Flow
```
[Login Request] → [Django Auth] → [Session Creation]
                      ↓
              [Permission Check] → [Access Grant/Deny]
```

### Authorization Levels
```python
ROLE_PERMISSIONS = {
    'ADMIN': ['all_permissions'],
    'DOCTOR': [
        'view_patient',
        'add_patient',
        'change_patient',
        'view_labs',
        'add_labs'
    ],
    'NURSE': [
        'view_patient',
        'add_vitals',
        'view_labs'
    ]
}
```

## Integration Architecture

### API Structure
```
api/v1/
├── patients/
│   ├── GET / - List patients
│   ├── POST / - Create patient
│   └── GET /{id}/ - Patient details
├── vitals/
│   ├── GET / - List vitals
│   └── POST / - Record vitals
└── labs/
    ├── GET / - List lab results
    └── POST / - Add lab results
```

## Deployment Architecture

### Production Environment
```
[Load Balancer]
      ↓
[Nginx Servers]
      ↓
[Django App Servers]
      ↓
[Database Cluster]
```

## Performance Optimization

### Database Optimization
- Indexed fields
- Query optimization
- Connection pooling

### Caching Strategy
- Page caching
- Object caching
- Query caching
- Session storage

## Related Documentation
- [[Development Guide]]
- [[API Reference]]
- [[Deployment Guide]]
- [[Security Guide]]

## Tags
#architecture #technical #django #documentation 