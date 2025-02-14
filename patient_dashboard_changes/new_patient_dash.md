# Patient Dashboard Optimization Plan

## Implementation Details

### Dependencies and Compatibility
```python
DEPENDENCIES = {
    # Core Requirements
    'django': '>=4.0.0',
    'python': '>=3.9.0',
    
    # Frontend Libraries
    'django-htmx': '>=1.9.10',
    'alpine.js': '>=3.13.5',
    
    # Performance & Monitoring
    'django-cacheops': '>=6.1',
    'django-debug-toolbar': '>=3.8.1',
    
    # Testing & Development
    'pytest': '>=7.3.1',
    'pytest-django': '>=4.5.2'
}

# Browser Compatibility
BROWSER_SUPPORT = {
    'chrome': '>=90',
    'firefox': '>=88',
    'safari': '>=14',
    'edge': '>=90'
}
```

### State Management
```javascript
// Dashboard State Management
const dashboardState = {
    // Tab State Management
    tabTransitions: {
        beforeSwitch: {
            actions: [
                'saveScrollPosition',
                'startLoadingState',
                'clearPreviousErrors'
            ],
            dataPreservation: ['unsavedFormData', 'filterSettings']
        },
        duringSwitch: {
            actions: [
                'fetchTabData',
                'updateCache',
                'validateIncomingData'
            ],
            errorHandling: ['retryOnFailure', 'fallbackToCache']
        },
        afterSwitch: {
            actions: [
                'restoreScrollPosition',
                'endLoadingState',
                'updateBrowserHistory'
            ],
            cleanup: ['removeStaleData', 'resetFormStates']
        }
    },
    
    // Form Interaction States
    formStates: {
        editing: {
            validateOnChange: true,
            autosave: {
                enabled: true,
                interval: 30000  // 30 seconds
            }
        },
        submitting: {
            optimisticUpdate: true,
            rollbackOnError: true
        }
    },
    
    // Cache Management
    cacheStrategy: {
        tabs: {
            ttl: 300,  // 5 minutes
            invalidateOn: ['dataUpdate', 'userAction']
        },
        patientData: {
            ttl: 600,  // 10 minutes
            prefetch: ['criticalInfo', 'recentMedications']
        }
    }
}
```

### API Contracts
```python
# Data Contracts for Tab Content
TAB_DATA_CONTRACTS = {
    'overview': {
        'required_fields': {
            'patient_info': {
                'id': 'uuid',
                'name': 'str',
                'dob': 'date',
                'status': 'str'
            },
            'recent_vitals': {
                'timestamp': 'datetime',
                'measurements': 'dict'
            },
            'alerts': 'list'
        },
        'optional_fields': {
            'notes': 'list',
            'upcoming_appointments': 'list'
        },
        'computed_fields': {
            'age': 'int',
            'risk_factors': 'list'
        }
    },
    'medications': {
        'required_fields': {
            'current_medications': {
                'id': 'uuid',
                'name': 'str',
                'dosage': 'str',
                'frequency': 'str',
                'prescriber': 'dict'
            },
            'allergies': 'list'
        },
        'optional_fields': {
            'medication_history': 'list',
            'interactions': 'list'
        },
        'permissions': {
            'edit': ['doctor', 'nurse'],
            'view': ['all_staff']
        }
    },
    'visits': {
        'required_fields': {
            'appointments': {
                'id': 'uuid',
                'date': 'datetime',
                'provider': 'dict',
                'type': 'str'
            }
        },
        'optional_fields': {
            'notes': 'list',
            'attachments': 'list'
        },
        'filters': {
            'date_range': 'tuple',
            'visit_type': 'list'
        }
    },
    'labs': {
        'required_fields': {
            'results': {
                'id': 'uuid',
                'test_name': 'str',
                'date': 'datetime',
                'value': 'float',
                'unit': 'str',
                'range': 'dict'
            }
        },
        'optional_fields': {
            'trending': 'dict',
            'flags': 'list'
        },
        'aggregations': {
            'by_panel': 'dict',
            'by_date': 'dict'
        }
    }
}

# Event Sourcing Contracts
EVENT_CONTRACTS = {
    'tab_view': {
        'user_id': 'uuid',
        'tab_name': 'str',
        'timestamp': 'datetime',
        'session_id': 'str'
    },
    'data_update': {
        'entity_type': 'str',
        'entity_id': 'uuid',
        'changes': 'dict',
        'user_id': 'uuid',
        'timestamp': 'datetime'
    }
}

# Cache Invalidation Rules
CACHE_INVALIDATION_RULES = {
    'patient_update': ['overview', 'demographics'],
    'medication_change': ['medications', 'overview'],
    'lab_result': ['labs', 'overview'],
    'visit_complete': ['visits', 'overview']
}
```

## Core Architecture

### 1. Dynamic Tab System

```html
<!-- Main container -->
<div class="card-dashboard"
     x-data="{ 
         activeTab: '{{ active_tab }}',
         loading: false,
         error: null,
         notifications: []
     }"
     @htmx:before-request="loading = true"
     @htmx:after-request="loading = false"
     @htmx:error="error = $event.detail.error"
     role="tablist"
     aria-label="Patient Information">
    <!-- Tab bar -->
    <nav class="pill-nav" aria-label="Patient sections">
        {% for tab in ['overview', 'visits', 'medications', 'labs'] %}
        <button @click="loadTab('{{ tab }}')"
                :class="{ 'active-pill': activeTab === '{{ tab }}' }"
                role="tab"
                :aria-selected="activeTab === '{{ tab }}'"
                :aria-controls="'{{ tab }}-panel'"
                id="{{ tab }}-tab">
            {{ tab|title }}
        </button>
        {% endfor %}
    </nav>
    
    <!-- Loading and Error States -->
    <div x-show="loading" class="loading-skeleton" role="status" aria-live="polite">
        Loading content...
    </div>
    <div x-show="error" class="error-message" role="alert">
        <p x-text="error"></p>
        <button @click="retryLoad()" class="btn-retry">Retry</button>
    </div>
    
    <!-- Content area -->
    <div id="tab-content" 
         class="animated-content"
         :aria-busy="loading"
         role="tabpanel"
         :aria-labelledby="activeTab + '-tab'">
        {% include active_partial %}
    </div>
</div>
```

### 2. Backend Optimization
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

## Implementation Checklist

1. **Dependencies**
```html
<!-- base.html -->
<script defer src="https://unpkg.com/htmx.org@1.9.10"></script>
<script defer src="https://unpkg.com/alpinejs@3.13.5/dist/cdn.min.js"></script>
<link rel="stylesheet" href="{% static 'css/dashboard.css' %}">
<link rel="stylesheet" href="{% static 'css/loading-states.css' %}">
```

2. **File Structure**
```
patient_records/
├── templates/
│   ├── patient_detail.html
│   └── partials/
│       ├── _overview.html
│       ├── _medications.html
│       ├── _visits.html
│       └── _error.html
├── static/
│   └── css/
│       ├── dashboard.css
│       └── loading-states.css
└── js/
    └── dashboard/
        ├── state.js
        └── accessibility.js
```

3. **Critical CSS**
```css
.pill-nav button {
    padding: 0.8rem 1.8rem;
    border-radius: 2rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.animated-content {
    transition: opacity 0.2s ease-in-out;
}

.card-grid {
    display: grid;
    gap: 1.2rem;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
}

.context-modal {
    backdrop-filter: blur(4px);
    background: rgba(255, 255, 255, 0.9);
}

/* Loading States */
.loading-skeleton {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: loading 1.5s infinite;
}

/* Error States */
.error-message {
    padding: 1rem;
    border-left: 4px solid #dc3545;
    background: #fff5f5;
    margin: 1rem 0;
}

/* Accessibility Focus States */
.pill-nav button:focus-visible {
    outline: 2px solid #4CAF50;
    outline-offset: 2px;
}

[role="tabpanel"]:focus {
    outline: none;
    box-shadow: 0 0 0 2px #4CAF50;
}
```

## Phase Implementation

1. **Phase 1: Core System**
- Tab navigation framework with ARIA roles
- HTMX content loading with error states
- Basic card layouts with loading skeletons

2. **Phase 2: Interaction Layer**
- In-context editing modals with validation
- Form validation with error messaging
- Real-time updates with optimistic UI
- Keyboard navigation support

3. **Phase 3: Optimization**
- Query caching with invalidation
- Scroll position preservation
- Loading skeletons and placeholders
- Error boundary implementation

4. **Phase 4: Polish**
- Micro-interactions and transitions
- Enhanced keyboard navigation
- Print styles and media queries
- Accessibility audit and fixes

## Validation Tests
```python
# test_views.py
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from time import time

class DashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.patient = Patient.objects.create(
            first_name="Test",
            last_name="Patient"
        )
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client.login(username='testuser', password='testpass')

    def test_tab_switch_performance(self):
        start = time()
        response = self.client.get(
            reverse('patient_detail', args=[self.patient.id]) + '?tab=medications',
            HTTP_HX_REQUEST='true'
        )
        self.assertLess(time() - start, 0.2)
        self.assertEqual(response.status_code, 200)
    
    def test_error_handling(self):
        with patch('patient_records.views.get_cached_patient_data') as mock_cache:
            mock_cache.side_effect = Exception("Test error")
            response = self.client.get(
                reverse('patient_detail', args=[self.patient.id]) + '?tab=medications',
                HTTP_HX_REQUEST='true'
            )
            self.assertEqual(response.status_code, 500)
            self.assertIn('error', response.json())
    
    def test_accessibility(self):
        response = self.client.get(reverse('patient_detail', args=[self.patient.id]))
        self.assertContains(response, 'role="tablist"')
        self.assertContains(response, 'aria-selected')
        self.assertContains(response, 'aria-controls')
    
    def test_cache_invalidation(self):
        # Test cache is properly invalidated after updates
        cache_key = f'patient_{self.patient.id}_medications'
        cache.set(cache_key, {'test': 'data'})
        
        response = self.client.post(
            reverse('add_medication', args=[self.patient.id]),
            {'medication': 'test_med'}
        )
        
        self.assertIsNone(cache.get(cache_key))
```

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

## Migration Plan

### Stage 0: Preparation
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

### Stage 1: Foundation
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

### Stage 2: Progressive Enhancement
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

### Stage 3: Data Migration & Validation
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

### Stage 4: Gradual Rollout
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

### Stage 5: Cleanup & Optimization
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

### Rollback Plan
```python
# Quick rollback middleware
class DashboardRollbackMiddleware:
    def process_request(self, request):
        if settings.DASHBOARD_EMERGENCY_ROLLBACK:
            return redirect(reverse('patient_detail_old', 
                          args=[request.resolver_match.kwargs['patient_id']]))
```

### Success Metrics
- Page load time < 2s
- Tab switch time < 200ms
- Error rate < 1%
- Cache hit ratio > 90%
- Zero critical accessibility issues

## Codebase Compatibility Analysis

### Current Architecture Alignment

1. **Event Sourcing Compatibility**
   - Existing `EventStore` and read models align with proposed caching strategy
   - Current `PatientReadModel` supports required tab data contracts
   - `ClinicalReadModel` provides foundation for clinical data aggregation

2. **Required Adaptations**

a. **Caching Configuration**
```python
# Add to settings.py
CACHING_CONFIG = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

b. **Event Sourcing Enhancement**
```python
# Add to models/event_sourcing.py
class TabViewEvent(models.Model):
    """Tracks tab view events for analytics and caching"""
    user_id = models.UUIDField()
    tab_name = models.CharField(max_length=50)
    session_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user_id', 'timestamp']),
            models.Index(fields=['tab_name', 'timestamp'])
        ]
```

3. **Implementation Strategy**

a. **Cache Invalidation Integration**
```python
# Add to models/audit/events.py
def invalidate_cache_for_event(sender, instance, **kwargs):
    if instance.event_type in CACHE_INVALIDATION_RULES:
        tabs_to_invalidate = CACHE_INVALIDATION_RULES[instance.event_type]
        for tab in tabs_to_invalidate:
            cache_key = f'patient_{instance.aggregate_id}_{tab}'
            cache.delete(cache_key)
```

b. **Required New Structure**
```
patient_records/
├── cache/
│   ├── __init__.py
│   ├── invalidation.py
│   └── strategies.py
├── state/
│   ├── __init__.py
│   ├── tab_manager.py
│   └── form_manager.py
└── monitoring/
    ├── __init__.py
    ├── metrics.py
    └── alerts.py
```

### Integration Points

1. **Model Layer**
   - Current event sourcing system supports all required data contracts
   - Read models provide necessary data aggregation
   - Existing audit trail system aligns with monitoring requirements

2. **View Layer**
   - New tab system can run parallel to existing views
   - HTMX integration requires minimal changes to base templates
   - Current URL structure supports new routing patterns

3. **Template Layer**
   - Existing templates can be gradually migrated
   - New partial templates can coexist with current structure
   - CSS enhancements build on current styling system

### Risk Assessment

1. **Low Risk Areas**
   - Event sourcing integration
   - Cache implementation
   - Frontend enhancements
   - Accessibility improvements

2. **Medium Risk Areas**
   - Cache invalidation timing
   - State management during tab switches
   - Performance during high load

3. **High Risk Areas**
   - Data consistency during transition
   - Complex query optimization
   - Real-time updates

### Mitigation Strategies

1. **Data Consistency**
```python
class DataConsistencyMiddleware:
    """Ensures data consistency between old and new views"""
    def process_response(self, request, response):
        if settings.ENABLE_CONSISTENCY_CHECK:
            old_data = self.get_old_view_data(request)
            new_data = self.get_new_view_data(request)
            if not self.validate_consistency(old_data, new_data):
                metrics.increment('data.consistency.error')
                logger.error(f"Data consistency error: {request.path}")
        return response
```

2. **Performance Monitoring**
```python
class PerformanceMonitor:
    """Tracks performance metrics during transition"""
    def __init__(self):
        self.metrics = defaultdict(list)

    def record_metric(self, metric_type, value):
        self.metrics[metric_type].append({
            'value': value,
            'timestamp': timezone.now()
        })
        
    def get_performance_report(self):
        return {
            metric: {
                'avg': statistics.mean(m['value'] for m in values),
                'p95': numpy.percentile([m['value'] for m in values], 95)
            }
            for metric, values in self.metrics.items()
        }
```

3. **Rollback Triggers**
```python
def should_rollback(request, error_rate, performance_metrics):
    """Determines if system should rollback based on metrics"""
    if error_rate > settings.MAX_ERROR_RATE:
        return True
    if performance_metrics['tab_switch'] > settings.MAX_TAB_SWITCH_TIME:
        return True
    return False
```

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

### Communication Protocol
1. **Status Updates**
   - Begin each session with current phase and task
   - End each session with summary of changes
   - Flag any blockers or concerns immediately

2. **Code Changes**
   - Always explain changes before implementing
   - Show relevant code snippets for context
   - Wait for confirmation on major changes

### Safety Requirements
1. **Code Analysis**
   - Always check existing code before modifications
   - Verify imports and dependencies
   - Confirm file structure matches plan

2. **Change Management**
   ```python
   # Example of safe code modification
   # 1. First show existing code
   # 2. Then explain changes
   # 3. Finally implement with proper error handling