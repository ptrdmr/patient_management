# API Reference

## Overview
This document provides detailed information about the Patient Management System's API endpoints, request/response formats, and authentication requirements.

## Authentication

### Token Authentication
```http
POST /api/token/
Content-Type: application/json

{
    "username": "user@example.com",
    "password": "secure_password"
}
```

Response:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbG..."
}
```

### Using Authentication
Include the token in request headers:
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## Patient Endpoints

### List Patients
```http
GET /api/patients/
```

Parameters:
- `search`: Search term for patient name/ID
- `page`: Page number for pagination
- `page_size`: Results per page

Response:
```json
{
    "count": 100,
    "next": "/api/patients/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "patient_number": "2023001",
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1980-01-01"
        }
    ]
}
```

### Patient Details
```http
GET /api/patients/{id}/
```

Response:
```json
{
    "id": 1,
    "patient_number": "2023001",
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1980-01-01",
    "gender": "M",
    "contact": {
        "address": "123 Main St",
        "phone": "(555) 555-5555",
        "email": "john@example.com"
    },
    "medical": {
        "allergies": ["Penicillin"],
        "code_status": "Full Code"
    }
}
```

## Clinical Data Endpoints

### Vital Signs
```http
POST /api/patients/{id}/vitals/
Content-Type: application/json

{
    "blood_pressure": "120/80",
    "temperature": 98.6,
    "spo2": 98,
    "pulse": 72,
    "respirations": 16
}
```

Response:
```json
{
    "id": 1,
    "patient_id": 1,
    "timestamp": "2023-12-03T10:30:00Z",
    "blood_pressure": "120/80",
    "temperature": 98.6,
    "spo2": 98,
    "pulse": 72,
    "respirations": 16
}
```

### Laboratory Results

#### CMP Labs
```http
POST /api/patients/{id}/labs/cmp/
Content-Type: application/json

{
    "sodium": 140,
    "potassium": 4.0,
    "chloride": 100,
    "co2": 24,
    "glucose": 85
}
```

#### CBC Labs
```http
POST /api/patients/{id}/labs/cbc/
Content-Type: application/json

{
    "wbc": 7.5,
    "rbc": 4.8,
    "hemoglobin": 14.2,
    "hematocrit": 42
}
```

## Medication Endpoints

### List Medications
```http
GET /api/patients/{id}/medications/
```

Response:
```json
{
    "count": 2,
    "results": [
        {
            "id": 1,
            "drug": "Metformin",
            "dose": "500mg",
            "frequency": "BID",
            "route": "PO",
            "active": true
        }
    ]
}
```

### Add Medication
```http
POST /api/patients/{id}/medications/
Content-Type: application/json

{
    "drug": "Metformin",
    "dose": "500mg",
    "frequency": "BID",
    "route": "PO",
    "prn": false
}
```

## Error Responses

### Validation Error
```json
{
    "status": "error",
    "code": 400,
    "message": "Validation failed",
    "errors": {
        "field_name": [
            "Error message"
        ]
    }
}
```

### Authentication Error
```json
{
    "status": "error",
    "code": 401,
    "message": "Authentication credentials were not provided"
}
```

## Pagination

All list endpoints support pagination with the following parameters:
- `page`: Page number (default: 1)
- `page_size`: Results per page (default: 20, max: 100)

Response format:
```json
{
    "count": 100,
    "next": "https://api.example.com/items/?page=3",
    "previous": "https://api.example.com/items/?page=1",
    "results": []
}
```

## Rate Limiting

- Authenticated requests: 100 requests per minute
- Unauthenticated requests: 20 requests per minute

Rate limit headers:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1701609600
```

## API Versioning

Version is specified in the URL:
```http
https://api.example.com/v1/patients/
```

## Related Documentation
- [[API Authentication|Authentication Guide]]
- [[API Versioning|Versioning Guide]]
- [[Rate Limiting|Rate Limit Documentation]]
- [[API Testing|Testing Guide]]

## Tags
#api #documentation #endpoints #django 