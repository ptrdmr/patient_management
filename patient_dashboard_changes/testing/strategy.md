# Testing Strategy

## Test Cases
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

## Data Consistency Tests
```python
class DataConsistencyTests(TestCase):
    def setUp(self):
        self.patient = Patient.objects.create(
            first_name="Test",
            last_name="Patient"
        )
        
    def test_read_model_sync(self):
        """Test that read models stay in sync with write models"""
        # Create a medication
        med = Medication.objects.create(
            patient=self.patient,
            name="Test Med",
            dosage="10mg"
        )
        
        # Verify read model is updated
        read_model = PatientReadModel.objects.get(id=self.patient.id)
        self.assertIn(med.id, [m['id'] for m in read_model.current_data['medications']])
        
    def test_cache_consistency(self):
        """Test that cache stays consistent with database"""
        # Add data to cache
        cache_key = f'patient_{self.patient.id}_medications'
        cache.set(cache_key, {'medications': []})
        
        # Update database
        med = Medication.objects.create(
            patient=self.patient,
            name="Test Med"
        )
        
        # Verify cache is invalidated
        self.assertIsNone(cache.get(cache_key))
```

## Performance Tests
```python
class PerformanceTests(TestCase):
    def setUp(self):
        self.patient = create_test_patient_with_data()
        
    def test_query_optimization(self):
        """Test that queries are optimized"""
        with self.assertNumQueries(3):  # Should only need 3 queries
            response = self.client.get(
                reverse('patient_detail', args=[self.patient.id]) + '?tab=medications'
            )
            
    def test_cache_hit_ratio(self):
        """Test cache effectiveness"""
        cache_key = f'patient_{self.patient.id}_medications'
        
        # First request - cache miss
        response = self.client.get(
            reverse('patient_detail', args=[self.patient.id]) + '?tab=medications'
        )
        
        # Second request - should be cache hit
        with self.assertNumQueries(0):  # No queries should be needed
            response = self.client.get(
                reverse('patient_detail', args=[self.patient.id]) + '?tab=medications'
            )
```

## Security Tests
```python
class SecurityTests(TestCase):
    def test_csrf_protection(self):
        """Test CSRF protection"""
        client = Client(enforce_csrf_checks=True)
        response = client.post(
            reverse('add_medication', args=[self.patient.id]),
            {'medication': 'test_med'}
        )
        self.assertEqual(response.status_code, 403)
        
    def test_permission_checks(self):
        """Test role-based access control"""
        # Create non-medical staff user
        user = User.objects.create_user(
            username='nonmedical',
            password='test'
        )
        self.client.login(username='nonmedical', password='test')
        
        response = self.client.post(
            reverse('add_medication', args=[self.patient.id]),
            {'medication': 'test_med'}
        )
        self.assertEqual(response.status_code, 403)
```

## Accessibility Tests
```python
class AccessibilityTests(TestCase):
    def test_aria_roles(self):
        """Test ARIA roles and labels"""
        response = self.client.get(reverse('patient_detail', args=[self.patient.id]))
        self.assertContains(response, 'role="tablist"')
        self.assertContains(response, 'aria-label="Patient sections"')
        
    def test_keyboard_navigation(self):
        """Test keyboard navigation support"""
        response = self.client.get(reverse('patient_detail', args=[self.patient.id]))
        self.assertContains(response, 'tabindex="0"')
        self.assertContains(response, 'role="tab"')
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