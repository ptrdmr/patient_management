# Security Implementation

## Overview
This document details the security measures implemented in the Patient Management System, with a focus on HIPAA compliance and medical data protection.

## Data Security

### PHI Protection
```python
class EncryptedPHIField(models.TextField):
    """Field for encrypting Protected Health Information"""
    def __init__(self, *args, **kwargs):
        self.key = settings.PHI_ENCRYPTION_KEY
        self.fernet = Fernet(self.key)
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        if value is None:
            return None
        return self.fernet.encrypt(value.encode()).decode()

    def from_db_value(self, value, *args):
        if value is None:
            return None
        return self.fernet.decrypt(value.encode()).decode()
```

### Medical Record Access Control
```python
class MedicalRecordAccess(models.Model):
    record = models.ForeignKey('MedicalRecord', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_type = models.CharField(max_length=20, choices=[
        ('READ', 'Read Only'),
        ('WRITE', 'Read/Write'),
        ('ADMIN', 'Full Access')
    ])
    granted_by = models.ForeignKey(User, related_name='access_granted', on_delete=models.SET_NULL, null=True)
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True)
```

## Access Control

### Role-Based Access
```python
ROLE_PERMISSIONS = {
    'DOCTOR': {
        'can_view_full_patient_history': True,
        'can_edit_medical_records': True,
        'can_prescribe_medications': True,
    },
    'NURSE': {
        'can_view_full_patient_history': True,
        'can_edit_medical_records': True,
        'can_prescribe_medications': False,
    },
    'STAFF': {
        'can_view_full_patient_history': False,
        'can_edit_medical_records': False,
        'can_view_demographics': True,
    }
}

def check_medical_record_access(user, record):
    """Check user's access level for medical records"""
    if not user.is_authenticated:
        return False
    
    if user.role == 'DOCTOR' and record.department in user.departments.all():
        return True
    
    if user.role == 'NURSE' and record.department == user.department:
        return True
    
    return False
```

## Audit Logging

### PHI Access Logging
```python
class PHIAccessLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    access_time = models.DateTimeField(auto_now_add=True)
    record_type = models.CharField(max_length=50)  # e.g., 'Patient', 'MedicalRecord'
    record_id = models.IntegerField()
    action = models.CharField(max_length=20)  # e.g., 'VIEW', 'EDIT', 'EXPORT'
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'access_time']),
            models.Index(fields=['record_type', 'record_id']),
        ]
```

### Audit Trail
```python
def log_phi_access(user, record_type, record_id, action, request):
    """Log all PHI access attempts"""
    PHIAccessLog.objects.create(
        user=user,
        record_type=record_type,
        record_id=record_id,
        action=action,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
```

## Session Security

### Session Management
```python
# settings.py
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_SECURITY_EXPIRE_AT_BROWSER_CLOSE = True
```

### Inactivity Timeout
```python
MIDDLEWARE = [
    # ...
    'django.contrib.sessions.middleware.SessionMiddleware',
    'session_security.middleware.SessionSecurityMiddleware',
]

SESSION_SECURITY_WARN_AFTER = 540  # 9 minutes
SESSION_SECURITY_EXPIRE_AFTER = 600  # 10 minutes
```

## Data Encryption

### Database Encryption
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'verify-full',
            'sslcert': '/path/to/client-cert.pem',
            'sslkey': '/path/to/client-key.pem',
            'sslrootcert': '/path/to/server-ca.pem',
        }
    }
}
```

## HIPAA Compliance

### Security Requirements
1. Access Controls
   - Role-based access
   - Minimum necessary access
   - Automatic logoff
2. Audit Controls
   - Activity logging
   - Access tracking
   - Change monitoring
3. Data Transmission
   - Encryption in transit
   - Secure protocols
4. Data Storage
   - Encryption at rest
   - Secure backups
5. Device and Media Controls
   - Mobile device management
   - Media disposal procedures

### Compliance Monitoring
```python
def check_hipaa_compliance():
    """Regular compliance check"""
    checks = {
        'encryption': check_encryption_status(),
        'access_logs': verify_access_logs(),
        'backup_status': check_backup_status(),
        'session_security': verify_session_settings(),
        'phi_protection': check_phi_fields(),
    }
    return all(checks.values()), checks
```

## Related Documentation
- [[Patient Records & Demographics]]
- [[Clinical Information Management]]
- [[API Security]]
- [[Compliance Guide]]

## Tags
#security #hipaa #encryption #compliance