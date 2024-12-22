# User Authentication & Authorization

## Overview
This document details the authentication and authorization system implemented in the Patient Management System, ensuring secure access control and user management.

## Authentication System

### User Model
```python
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Additional fields
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey('Department', on_delete=models.PROTECT)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    requires_password_change = models.BooleanField(default=True)
    last_password_change = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        permissions = [
            ("can_view_patient_records", "Can view patient records"),
            ("can_edit_patient_records", "Can edit patient records"),
            ("can_view_lab_results", "Can view lab results"),
            ("can_enter_orders", "Can enter orders"),
        ]
```

### Authentication Backend
```python
from django.contrib.auth.backends import ModelBackend

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                if user.requires_password_change:
                    raise PasswordChangeRequired()
                return user
        except User.DoesNotExist:
            return None
```

## Authorization System

### Role Definitions
```python
ROLE_CHOICES = [
    ('ADMIN', 'Administrator'),
    ('DOCTOR', 'Doctor'),
    ('NURSE', 'Nurse'),
    ('LAB_TECH', 'Laboratory Technician'),
    ('STAFF', 'Staff'),
]

ROLE_PERMISSIONS = {
    'ADMIN': [
        'all_permissions'
    ],
    'DOCTOR': [
        'view_patient_records',
        'edit_patient_records',
        'view_lab_results',
        'enter_orders'
    ],
    'NURSE': [
        'view_patient_records',
        'edit_patient_records',
        'view_lab_results'
    ],
    'LAB_TECH': [
        'view_lab_results',
        'enter_lab_results'
    ],
    'STAFF': [
        'view_patient_records'
    ]
}
```

### Permission Decorators
```python
from functools import wraps
from django.core.exceptions import PermissionDenied

def requires_permission(permission):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.has_perm(permission):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

@requires_permission('can_view_patient_records')
def view_patient(request, patient_id):
    # View implementation
    pass
```

## Security Measures

### Password Policy
```python
# settings.py
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

PASSWORD_EXPIRY_DAYS = 90
PASSWORD_HISTORY_COUNT = 5
```

### Session Management
```python
# settings.py
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
```

## Access Control

### View Protection
```python
from django.contrib.auth.mixins import UserPassesTestMixin

class DoctorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == 'DOCTOR'

class PatientUpdateView(DoctorRequiredMixin, UpdateView):
    model = Patient
    template_name = 'patient_update.html'
```

### API Protection
```python
from rest_framework.permissions import BasePermission

class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'DOCTOR'

class PatientViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsDoctor]
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
```

## Audit Trail

### Login Tracking
```python
class LoginAudit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    success = models.BooleanField()
```

### Activity Logging
```python
class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    resource_type = models.CharField(max_length=50)
    resource_id = models.IntegerField()
    details = models.JSONField()
```

## Multi-Factor Authentication

### MFA Configuration
```python
from django_otp.plugins.otp_totp.models import TOTPDevice

def setup_mfa(user):
    device = user.totpdevice_set.create(name='Default')
    return device.config_url

def verify_mfa(user, token):
    device = user.totpdevice_set.first()
    return device.verify_token(token)
```

## Related Documentation
- [[Security Implementation]]
- [[API Security]]
- [[Audit System]]
- [[Password Policies]]

## Tags
#security #authentication #authorization #access-control 