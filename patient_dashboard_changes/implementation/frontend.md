# Frontend Implementation

## Dynamic Tab System

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

## Critical CSS
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

## File Structure
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