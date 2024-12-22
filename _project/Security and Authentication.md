# Security and Authentication

## Overview
This document outlines the security measures and authentication systems implemented in the Patient Management System. Security is paramount given the sensitive nature of medical data.

## Authentication System

### User Authentication
```python
# settings.py
AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_COOKIE_SECURE = True
```

### Custom User Model
```python
class User(AbstractUser):
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    department = models.CharField(max_length=50)
    last_password_change = models.DateTimeField(auto_now=True)
    require_password_change = models.BooleanField(default=False)
```

## Authorization

### Permission Classes
```python
class RoleBasedPermission:
    """Role-based access control"""
    def has_permission(self, request, view):
        return request.user.role in self.allowed_roles
```

### Role Definitions
```python
ROLE_CHOICES = [
    ('ADMIN', 'Administrator'),
    ('DOCTOR', 'Doctor'),
    ('NURSE', 'Nurse'),
    ('STAFF', 'Staff')
]
```

## Security Middleware

### Security Headers
```python
# settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'patient_records.middleware.SecurityHeadersMiddleware',
]
```

### Custom Security Middleware
```python
class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['Strict-Transport-Security'] = 'max-age=31536000'
        return response
```

## Password Management

### Password Validation
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
```

### Password Reset Flow
```python
class PasswordResetView(FormView):
    """Secure password reset implementation"""
    template_name = 'accounts/password_reset.html'
    form_class = PasswordResetForm
    success_url = reverse_lazy('password_reset_done')
```

## Session Management

### Session Settings
```python
# settings.py
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
```

### Session Cleanup
```python
@periodic_task(run_every=timedelta(hours=1))
def cleanup_expired_sessions():
    """Remove expired sessions from database"""
    Session.objects.filter(expire_date__lt=timezone.now()).delete()
```

## Audit Trail

### Activity Logging
```python
class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    details = models.JSONField()
```

### Audit Middleware
```python
class AuditMiddleware:
    """Log all significant actions"""
    def __call__(self, request):
        response = self.get_response(request)
        if hasattr(request, 'user') and request.user.is_authenticated:
            AuditLog.objects.create(
                user=request.user,
                action=request.method,
                ip_address=request.META.get('REMOTE_ADDR'),
                details={
                    'path': request.path,
                    'method': request.method,
                }
            )
        return response
```

## Data Protection

### Encryption at Rest
```python
# settings.py
FIELD_ENCRYPTION_KEY = config('ENCRYPTION_KEY')

class EncryptedTextField(models.TextField):
    """Field for storing encrypted data"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fernet = Fernet(FIELD_ENCRYPTION_KEY)
```

### Data Masking
```python
def mask_ssn(ssn):
    """Mask sensitive data for display"""
    return f"XXX-XX-{ssn[-4:]}" if ssn else ""
```

## Security Best Practices

### CSRF Protection
- Token validation
- Secure cookie handling
- Form protection

### XSS Prevention
- Content Security Policy
- Input sanitization
- Output escaping

### SQL Injection Prevention
- Parameterized queries
- ORM usage
- Input validation

## Related Documentation
- [[Authentication|User Authentication Guide]]
- [[Authorization|Access Control Guide]]
- [[Encryption|Data Encryption Guide]]
- [[Audit|Audit System Guide]]

## Security Checklist
- [ ] SSL/TLS enabled
- [ ] Password policies enforced
- [ ] Session management configured
- [ ] CSRF protection enabled
- [ ] XSS prevention implemented
- [ ] SQL injection protection
- [ ] Audit logging active
- [ ] Data encryption configured

## Tags
#security #authentication #django #documentation 