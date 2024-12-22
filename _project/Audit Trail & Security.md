# Audit Trail & Security

## Overview
The Audit Trail & Security module provides comprehensive tracking of all system activities and security measures to ensure HIPAA compliance.

## Audit System

### Activity Logging
```python
class AuditLog(models.Model):
    """Model for tracking system activities."""
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True
    )
    
    # Action details
    action = models.CharField(
        max_length=20,
        choices=[
            ('CREATE', 'Create'),
            ('READ', 'Read'),
            ('UPDATE', 'Update'),
            ('DELETE', 'Delete'),
            ('LOGIN', 'Login'),
            ('LOGOUT', 'Logout'),
            ('EXPORT', 'Export'),
            ('IMPORT', 'Import')
        ]
    )
    
    # Resource information
    resource_type = models.CharField(max_length=50)
    resource_id = models.CharField(max_length=50)
    
    # Request details
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    request_method = models.CharField(max_length=10)
    request_path = models.CharField(max_length=255)
    
    # Changes
    changes = models.JSONField(null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['timestamp', 'action']),
            models.Index(fields=['resource_type', 'resource_id']),
            models.Index(fields=['user', 'timestamp']),
        ]
```

### Audit Middleware
```python
class AuditMiddleware:
    """Middleware to automatically log system activities."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Process request
        response = self.get_response(request)
        
        # Log the activity
        if hasattr(request, 'user') and request.user.is_authenticated:
            self.log_activity(request, response)
        
        return response
    
    def log_activity(self, request, response):
        """Log the request activity."""
        # Determine action type
        if request.method == 'GET':
            action = 'READ'
        elif request.method == 'POST':
            action = 'CREATE'
        elif request.method in ['PUT', 'PATCH']:
            action = 'UPDATE'
        elif request.method == 'DELETE':
            action = 'DELETE'
        
        # Create audit log
        AuditLog.objects.create(
            user=request.user,
            action=action,
            resource_type=self.get_resource_type(request),
            resource_id=self.get_resource_id(request),
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            request_method=request.method,
            request_path=request.path,
            changes=self.get_changes(request)
        )
```

## Security Monitoring

### Security Events
```python
class SecurityEvent(models.Model):
    """Model for tracking security-related events."""
    timestamp = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(
        max_length=50,
        choices=[
            ('AUTH_FAILURE', 'Authentication Failure'),
            ('BRUTE_FORCE', 'Brute Force Attempt'),
            ('UNAUTHORIZED_ACCESS', 'Unauthorized Access'),
            ('SESSION_HIJACK', 'Session Hijacking Attempt'),
            ('DATA_EXPORT', 'Sensitive Data Export'),
            ('CONFIGURATION_CHANGE', 'Security Configuration Change')
        ]
    )
    severity = models.CharField(
        max_length=20,
        choices=[
            ('LOW', 'Low'),
            ('MEDIUM', 'Medium'),
            ('HIGH', 'High'),
            ('CRITICAL', 'Critical')
        ]
    )
    description = models.TextField()
    user = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True
    )
    ip_address = models.GenericIPAddressField()
    additional_data = models.JSONField(null=True)
```

### Security Monitoring
```python
def monitor_security_events():
    """Monitor and analyze security events."""
    # Check for authentication failures
    auth_failures = SecurityEvent.objects.filter(
        event_type='AUTH_FAILURE',
        timestamp__gte=timezone.now() - timedelta(minutes=5)
    ).values('ip_address').annotate(
        failure_count=Count('id')
    )
    
    # Check for brute force attempts
    for failure in auth_failures:
        if failure['failure_count'] >= 5:
            SecurityEvent.objects.create(
                event_type='BRUTE_FORCE',
                severity='HIGH',
                description=f"Multiple authentication failures from {failure['ip_address']}",
                ip_address=failure['ip_address']
            )
            block_ip_address(failure['ip_address'])

def block_ip_address(ip_address):
    """Block an IP address due to suspicious activity."""
    BlockedIP.objects.create(
        ip_address=ip_address,
        reason='Brute force attempt',
        blocked_until=timezone.now() + timedelta(hours=24)
    )
```

## Access Control

### Role-Based Access
```python
class SecurityRole(models.Model):
    """Model for security roles and permissions."""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    permissions = models.ManyToManyField('Permission')
    
    # Role hierarchy
    parent_role = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    
    def has_permission(self, permission_name):
        """Check if role has specific permission."""
        if self.permissions.filter(codename=permission_name).exists():
            return True
        
        if self.parent_role:
            return self.parent_role.has_permission(permission_name)
        
        return False
```

## Compliance Reporting

### HIPAA Compliance Report
```python
def generate_hipaa_compliance_report(start_date, end_date):
    """Generate HIPAA compliance report."""
    report = {
        'period': {
            'start': start_date,
            'end': end_date
        },
        'access_summary': analyze_access_patterns(start_date, end_date),
        'security_events': analyze_security_events(start_date, end_date),
        'data_access': analyze_phi_access(start_date, end_date),
        'system_changes': analyze_system_changes(start_date, end_date)
    }
    
    return report

def analyze_phi_access(start_date, end_date):
    """Analyze PHI access patterns."""
    phi_access = AuditLog.objects.filter(
        timestamp__range=(start_date, end_date),
        resource_type__in=['Patient', 'MedicalRecord']
    ).values('user', 'action').annotate(
        access_count=Count('id')
    )
    
    return {
        'total_phi_access': phi_access.count(),
        'access_by_role': analyze_access_by_role(phi_access),
        'unusual_patterns': detect_unusual_patterns(phi_access)
    }
```

## Related Documentation
- [[Security Implementation]]
- [[User Authentication & Authorization]]
- [[API Security]]
- [[Compliance Guide]]

## Tags
#security #audit #compliance #hipaa 