# Patient Dashboard Core Architecture

## Dependencies and Compatibility
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

## State Management
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

## API Contracts
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