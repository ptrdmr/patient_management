# Backend Implementation

## View Layer
```python
from django.core.cache import cache
from django.views.decorators.http import require_http_methods
from typing import Dict, Optional

class TabDataError(Exception):
    pass

def get_cached_patient_data(patient_id: int, tab: str) -> Optional[Dict]:
    """
    Get cached patient data with error handling and typing
    """
    cache_key = f'patient_{patient_id}_{tab}'
    try:
        data = cache.get(cache_key)
        if not data:
            data = fetch_tab_data(patient_id, tab)
            cache.set(cache_key, data, timeout=300)  # 5 minute cache
        return data
    except Exception as e:
        logger.error(f"Cache error for patient {patient_id}, tab {tab}: {str(e)}")
        return None

@require_http_methods(["GET"])
def patient_detail(request, patient_id):
    try:
        patient = get_object_or_404(PatientReadModel, id=patient_id)
        tab_handlers = {
            'medications': lambda: Medication.objects.filter(patient=patient)
                .select_related('prescriber')
                .prefetch_related('interactions'),
            'visits': lambda: Visits.objects.filter(patient=patient)
                .prefetch_related('documents', 'providers'),
            'labs': lambda: {
                'cbc': CbcLabs.objects.filter(patient=patient).select_related(),
                'cmp': CmpLabs.objects.filter(patient=patient).select_related()
            }
        }

        if request.htmx:
            active_tab = request.GET.get('tab', 'overview')
            context = {'patient': patient}
            
            try:
                if handler := tab_handlers.get(active_tab):
                    context[active_tab] = get_cached_patient_data(patient_id, active_tab) or handler()
                return render(request, f"partials/{active_tab}.html", context)
            except Exception as e:
                logger.error(f"Error loading tab {active_tab} for patient {patient_id}: {str(e)}")
                return JsonResponse({
                    'error': 'Failed to load tab content',
                    'details': str(e)
                }, status=500)

        return render(request, 'patient_detail.html', {
            'patient': patient,
            'active_tab': 'overview'
        })
    except Exception as e:
        logger.error(f"Error in patient_detail view: {str(e)}")
        raise
```

## Performance Monitoring

1. **Metrics to Track**
- Page load time
- Time to first byte
- Tab switch latency
- Cache hit ratio
- Error rate by type

2. **Optimization Targets**
- < 200ms tab switch time
- < 2s initial page load
- > 90% cache hit ratio
- < 1% error rate

## Security Considerations

1. **Data Protection**
- Implement proper CSRF protection
- Sanitize all user inputs
- Use content security policy headers
- Implement rate limiting on API endpoints

2. **Access Control**
- Implement proper role-based access
- Audit logging for sensitive operations
- Session management and timeout
- API authentication and authorization

3. **Error Handling**
- Sanitize error messages
- Implement proper logging
- Use error boundaries
- Handle edge cases gracefully

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