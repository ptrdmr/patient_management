# Patient Records & Demographics

## Overview
This document details the patient records and demographics management system, including data structure, workflows, and best practices.

## Patient Data Model

### Core Demographics
```python
class Patient(models.Model):
    # Basic Information
    patient_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    
    # Contact Information
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(null=True, blank=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=200)
    emergency_contact_phone = models.CharField(max_length=20)
    emergency_contact_relation = models.CharField(max_length=50)
    
    # Medical Information
    blood_type = models.CharField(max_length=5, choices=BLOOD_TYPE_CHOICES)
    allergies = models.TextField(blank=True)
    code_status = models.CharField(max_length=50)
```

## Data Entry Workflows

### New Patient Registration
1. Verify patient identity
2. Enter basic demographics
3. Collect contact information
4. Record medical history
5. Assign patient ID
6. Create electronic record

### Record Updates
1. Search for patient record
2. Verify patient identity
3. Update relevant information
4. Document reason for change
5. Save with audit trail

## Data Validation

### Required Fields
- Patient ID
- First Name
- Last Name
- Date of Birth
- Gender
- Primary Contact Number
- Emergency Contact

### Validation Rules
```python
def clean_date_of_birth(self):
    """Validate date of birth"""
    dob = self.cleaned_data['date_of_birth']
    if dob > date.today():
        raise ValidationError("Date of birth cannot be in future")
    return dob

def clean_phone(self):
    """Validate phone number format"""
    phone = self.cleaned_data['phone']
    if not re.match(r'^\+?1?\d{9,15}$', phone):
        raise ValidationError("Invalid phone number format")
    return phone
```

## Search Functionality

### Search Parameters
- Patient ID
- Name (First/Last)
- Date of Birth
- Phone Number
- Email Address

### Search Implementation
```python
def search_patients(query):
    """Search patient records"""
    return Patient.objects.filter(
        Q(patient_id__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(phone__icontains=query) |
        Q(email__icontains=query)
    )
```

## Privacy & Security

### Data Protection
- Field-level encryption for sensitive data
- Access control based on user roles
- Audit logging for all changes
- Data masking in displays

### HIPAA Compliance
- Secure data transmission
- Access controls
- Audit trails
- Data encryption
- Secure backup

## Related Documentation
- [[Clinical Data]]
- [[Medical History]]
- [[Patient Search]]
- [[Data Privacy]]

## Tags
#patient-records #demographics #medical-data 