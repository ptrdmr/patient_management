# Current Limitations

## Overview
This document outlines the current limitations, constraints, and known issues in the Patient Management System.

## Technical Limitations

### Database Constraints
```python
# Maximum concurrent connections
MAX_DB_CONNECTIONS = 100

# Query timeout settings
STATEMENT_TIMEOUT = '30s'
IDLE_IN_TRANSACTION_SESSION_TIMEOUT = '60s'

# Connection pool settings
DATABASE_POOL_ARGS = {
    'max_overflow': 10,
    'pool_size': 5,
    'recycle': 300
}
```

### Performance Limits
- Maximum concurrent users: 500
- Maximum file upload size: 100MB
- Maximum report size: 1000 records
- API rate limit: 1000 requests per hour
- Search results pagination: 100 items per page
- Maximum batch processing size: 1000 records

### Memory Usage
```python
# Memory monitoring thresholds
MEMORY_THRESHOLDS = {
    'warning': 80,  # 80% usage
    'critical': 90  # 90% usage
}

def check_memory_usage():
    """Monitor memory usage."""
    memory = psutil.virtual_memory()
    if memory.percent >= MEMORY_THRESHOLDS['critical']:
        raise MemoryError("Critical memory usage")
    elif memory.percent >= MEMORY_THRESHOLDS['warning']:
        log.warning("High memory usage")
```

## Feature Limitations

### Patient Records
- Single primary care provider per patient
- Limited to one active insurance policy
- Maximum of 100 allergies per patient
- Maximum of 50 medications per patient
- File attachments limited to common formats (PDF, JPEG, PNG)

### Lab Results
```python
# Lab result limitations
LAB_RESULT_LIMITS = {
    'max_results_per_day': 10,
    'max_panels_per_order': 5,
    'retention_period_days': 365,
    'max_comments_length': 1000
}

class LabResult(models.Model):
    """Lab result model with limitations."""
    result_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(-9999.99),
            MaxValueValidator(9999.99)
        ]
    )
    comments = models.TextField(
        max_length=LAB_RESULT_LIMITS['max_comments_length']
    )
```

### Medical Imaging
- Maximum image resolution: 4096x4096
- Supported formats: DICOM, JPEG, PNG
- Maximum study size: 1GB
- Maximum series per study: 100
- Storage retention: 7 years

### Reporting
```python
# Report generation limits
REPORT_LIMITS = {
    'max_pages': 500,
    'max_records': 1000,
    'timeout_seconds': 300,
    'export_formats': ['PDF', 'CSV', 'XLSX']
}

def generate_report(parameters):
    """Generate report with limitations."""
    if len(parameters['records']) > REPORT_LIMITS['max_records']:
        raise ValueError("Exceeds maximum records limit")
    
    start_time = time.time()
    while time.time() - start_time < REPORT_LIMITS['timeout_seconds']:
        # Report generation logic
        pass
    
    raise TimeoutError("Report generation timeout")
```

## Security Constraints

### Authentication
- Password expiry: 90 days
- Maximum failed login attempts: 5
- Session timeout: 30 minutes
- Multi-factor authentication required for sensitive operations
- Password complexity requirements enforced

### Access Control
```python
# Access control limitations
ACCESS_LIMITS = {
    'max_roles_per_user': 3,
    'max_permissions_per_role': 50,
    'max_concurrent_sessions': 2
}

def check_access_limits(user):
    """Check user access limits."""
    if user.roles.count() >= ACCESS_LIMITS['max_roles_per_user']:
        raise ValidationError("Maximum roles limit reached")
    
    if user.sessions.count() >= ACCESS_LIMITS['max_concurrent_sessions']:
        raise ValidationError("Maximum concurrent sessions reached")
```

## Integration Limitations

### External Systems
- Limited to HL7 v2.x messages
- Maximum message size: 1MB
- Rate limit: 100 messages per minute
- Supported protocols: HTTPS, SFTP
- Timeout: 30 seconds per request

### API Constraints
```python
# API limitations
API_LIMITS = {
    'rate_limit': '1000/hour',
    'max_payload_size': 5 * 1024 * 1024,  # 5MB
    'max_batch_size': 100,
    'timeout_seconds': 30
}

class APIRateThrottle(UserRateThrottle):
    """API rate limiting."""
    rate = API_LIMITS['rate_limit']
    
    def allow_request(self, request, view):
        if request.user.is_staff:
            return True
        return super().allow_request(request, view)
```

## Browser Support

### Supported Browsers
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+
- Mobile browsers with limitations

### Browser Limitations
```javascript
// Browser feature detection
const BROWSER_REQUIREMENTS = {
    localStorage: true,
    webSockets: true,
    webWorkers: true,
    indexedDB: true
};

function checkBrowserSupport() {
    const missing = [];
    
    if (!window.localStorage) {
        missing.push('localStorage');
    }
    if (!window.WebSocket) {
        missing.push('webSockets');
    }
    if (!window.Worker) {
        missing.push('webWorkers');
    }
    if (!window.indexedDB) {
        missing.push('indexedDB');
    }
    
    return missing;
}
```

## Planned Improvements

### Short-term Fixes
- Increase database connection pool
- Optimize large report generation
- Enhance concurrent user support
- Improve file upload handling
- Add support for additional lab formats

### Long-term Solutions
- Implement microservices architecture
- Add distributed caching
- Enhance scalability
- Improve integration capabilities
- Add support for more image formats

## Related Documentation
- [[Performance Optimization]]
- [[Security Implementation]]
- [[System Architecture Overview]]
- [[Future Development]]

## Tags
#limitations #constraints #known-issues #performance 