# Migration Plan

## Stage 0: Preparation
1. **Environment Setup**
```bash
# Create new feature branch
git checkout -b feature/dashboard-optimization

# Install new dependencies
pip install django-htmx
```

2. **Backup & Documentation**
   - Take snapshot of production database
   - Document current performance metrics as baseline
   - Create rollback plan

## Stage 1: Foundation
1. **Static Assets Integration**
   - Add HTMX and Alpine.js to base template
   - Create new CSS structure
   - Implement loading states CSS

2. **Basic Infrastructure**
```python
# Create new template structure
patient_records/
├── templates/
│   ├── patient_detail_new.html      # New template alongside existing
│   └── partials/
│       ├── _overview.html           # Start with one tab
│       └── _error.html              # Error handling partial
```

3. **Initial Backend Changes**
```python
# Add new view alongside existing
@require_http_methods(["GET"])
def patient_detail_new(request, patient_id):
    """New view running in parallel with old one"""
    try:
        patient = get_object_or_404(PatientReadModel, id=patient_id)
        return render(request, 'patient_detail_new.html', {
            'patient': patient,
            'active_tab': 'overview'
        })
    except Exception as e:
        logger.error(f"Error in new patient_detail view: {str(e)}")
        raise
```

## Stage 2: Progressive Enhancement
1. **Tab System Implementation**
```python
# URLs configuration
path('patient/<int:patient_id>/new/', views.patient_detail_new, name='patient_detail_new'),
path('patient/<int:patient_id>/tab/<str:tab>/', views.load_tab, name='load_tab'),
```

2. **Caching Layer**
```python
# Implement caching with feature flag
ENABLE_DASHBOARD_CACHING = getattr(settings, 'ENABLE_DASHBOARD_CACHING', False)

def get_cached_patient_data(patient_id: int, tab: str) -> Optional[Dict]:
    if not ENABLE_DASHBOARD_CACHING:
        return None
    # Implementation as per new design
```

3. **Testing Infrastructure**
   - Set up test cases for new functionality
   - Implement performance monitoring

## Stage 3: Data Migration & Validation
1. **Data Verification**
```python
# Add validation middleware
class DataValidationMiddleware:
    def process_response(self, request, response):
        if 'validate_data' in request.GET:
            # Compare old vs new view data
            old_data = get_old_view_data(request)
            new_data = get_new_view_data(request)
            log_data_differences(old_data, new_data)
        return response
```

2. **Performance Testing**
   - Run load tests on staging
   - Validate caching behavior
   - Monitor error rates

## Stage 4: Gradual Rollout
1. **Feature Flag Implementation**
```python
# Add feature flag middleware
def use_new_dashboard(request):
    # Start with staff users
    if request.user.is_staff:
        return True
    # Gradually increase based on user ID
    return (hash(request.user.id) % 100) < settings.NEW_DASHBOARD_PERCENTAGE
```

2. **Monitoring & Metrics**
```python
# Add monitoring decorator
def monitor_dashboard_performance(view_func):
    def wrapper(request, *args, **kwargs):
        start_time = time.time()
        try:
            response = view_func(request, *args, **kwargs)
            metrics.timing('dashboard.load_time', time.time() - start_time)
            return response
        except Exception as e:
            metrics.increment('dashboard.errors')
            raise
    return wrapper
```

## Stage 5: Cleanup & Optimization
1. **Code Cleanup**
```python
# Remove old implementation
class RemoveOldDashboardMiddleware:
    def process_request(self, request):
        if 'old_dashboard' in request.GET:
            messages.warning(request, 'The old dashboard has been deprecated')
        return None
```

2. **Performance Optimization**
   - Fine-tune cache timeouts
   - Optimize database queries
   - Implement remaining accessibility features

## Rollback Plan
```python
# Quick rollback middleware
class DashboardRollbackMiddleware:
    def process_request(self, request):
        if settings.DASHBOARD_EMERGENCY_ROLLBACK:
            return redirect(reverse('patient_detail_old', 
                          args=[request.resolver_match.kwargs['patient_id']]))
```

## Success Metrics
- Page load time < 2s
- Tab switch time < 200ms
- Error rate < 1%
- Cache hit ratio > 90%
- Zero critical accessibility issues

### Core Safety Framework ⚠️
**EVERY action must follow these principles:**

1. **Verify First, Act Second**
   - ALWAYS check existing code before ANY changes
   - ALWAYS verify dependencies and imports
   - NEVER assume code structure or functionality
   - When in doubt, ASK first

2. **Incremental Changes Only**
   - Make ONE logical change at a time
   - Test EACH change before proceeding
   - Keep changes SMALL and FOCUSED
   - Maintain working state at all times

3. **Protect Sensitive Data**
   - Treat ALL patient-related code as PHI
   - NEVER expose sensitive information
   - ALWAYS maintain HIPAA compliance
   - When unsure about sensitivity, ASK

4. **Constant Verification**
   - VERIFY before each change
   - VERIFY after each change
   - VERIFY all dependencies
   - VERIFY all imports

5. **Stop Conditions**
   IMMEDIATELY STOP and ASK when encountering:
   - Unclear requirements
   - Security implications
   - Data integrity risks
   - Performance impacts
   - Complex dependencies
   - Missing documentation
   - Inconsistent patterns

6. **Change Scale Guide**
   ```
   GREEN  - Simple, isolated changes (proceed with normal checks)
   YELLOW - Multiple files affected (extra verification needed)
   RED    - Core functionality changes (requires explicit approval)
   ```
``` 