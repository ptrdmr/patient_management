# Models and Data Structure

## Overview
This document details the database schema and data models used in the Patient Management System. Each model is designed to handle specific aspects of patient care and medical record management.

## Core Models

### Patient Model
```python
class Patient:
    # Demographics
    id: AutoField(primary_key)
    first_name: CharField
    last_name: CharField
    date_of_birth: DateField
    gender: CharField(choices)
    
    # Contact
    address: CharField
    phone: CharField
    email: EmailField
    
    # Medical
    allergies: TextField
    code_status: CharField
    
    # Administrative
    created_at: DateTimeField
    updated_at: DateTimeField
    patient_number: CharField(unique)
```
→ [[Patient Model Details|Full Patient Model Documentation]]

### Clinical Data Models

#### Vitals
```python
class Vitals:
    patient: ForeignKey(Patient)
    date: DateField
    blood_pressure: CharField
    temperature: FloatField
    spo2: FloatField
    pulse: IntegerField
    respirations: IntegerField
```
→ [[Vitals Model|Vitals Documentation]]

#### Laboratory Results
```python
class CmpLabs:
    patient: ForeignKey(Patient)
    date: DateField
    # Comprehensive Metabolic Panel fields
    sodium: FloatField
    potassium: FloatField
    chloride: FloatField
    # ... other fields

class CbcLabs:
    patient: ForeignKey(Patient)
    date: DateField
    # Complete Blood Count fields
    wbc: FloatField
    rbc: FloatField
    hemoglobin: FloatField
    # ... other fields
```
→ [[Lab Models|Laboratory Models Documentation]]

### Medication Management
```python
class Medications:
    patient: ForeignKey(Patient)
    date_prescribed: DateField
    drug: CharField
    dose: CharField
    frequency: CharField
    route: CharField
    prn: BooleanField
    dc_date: DateField(null=True)
```
→ [[Medication Model|Medication Tracking Documentation]]

## Supporting Models

### Provider Management
```python
class Provider:
    name: CharField
    specialty: CharField
    contact: CharField
    active: BooleanField
```
→ [[Provider Model|Provider Documentation]]

### Audit Trail
```python
class AuditTrail:
    patient: ForeignKey(Patient)
    user: ForeignKey(User)
    action: CharField
    timestamp: DateTimeField
    changes: JSONField
```
→ [[Audit Model|Audit System Documentation]]

## Relationships

### One-to-Many
- Patient → Vitals
- Patient → Lab Results
- Patient → Medications
- Provider → Patients

### Many-to-Many
- Patients ↔ Providers
- Medications ↔ Allergies

## Data Validation
- [[Data Validation|Validation Rules]]
- [[Form Validation|Form Validation Logic]]
- [[Model Validation|Model-level Validation]]

## Database Indexes
- Patient lookup by ID
- Lab results by date
- Medication tracking
- Audit trail queries

## Data Migration
- [[Data Migration|Migration Procedures]]
- [[Schema Updates|Database Updates]]
- [[Data Backup|Backup Procedures]]

## Related Documentation
- [[Database Schema|Complete Schema Reference]]
- [[Model API|Model Usage Guide]]
- [[Query Optimization|Performance Tips]]
- [[Data Security|Security Measures]]

## Tags
#models #database #schema #documentation
