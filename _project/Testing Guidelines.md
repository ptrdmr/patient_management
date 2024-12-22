# Testing Guidelines

## Overview
This document outlines the testing standards and practices for the Patient Input Application, ensuring code reliability and quality through comprehensive testing.

## Test Structure

### Directory Organization
```
patient_records/
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_forms.py
│   └── test_api.py
```

### Base Test Classes
```python
from django.test import TestCase
from django.urls import reverse
from patient_records.models import PatientDemographics, Diagnosis, Vitals

class PatientRecordTestCase(TestCase):
    """Base test case for patient record tests."""
    
    def setUp(self):
        """Set up test data."""
        self.patient = PatientDemographics.objects.create(
            patient_id="TEST001",
            allergies="None known",
            code_status="Full Code"
        )
        
        self.diagnosis = Diagnosis.objects.create(
            patient_id=self.patient.patient_id,
            diagnosis="Hypertension",
            icd_code="I10"
        )
        
        self.vitals = Vitals.objects.create(
            patient_id=self.patient.patient_id,
            blood_pressure="120/80",
            temperature=98.6,
            pulse=72
        )
```

## Types of Tests

### Model Tests
```python
class PatientDemographicsTests(PatientRecordTestCase):
    """Tests for PatientDemographics model."""
    
    def test_patient_creation(self):
        """Test patient demographics creation."""
        self.assertEqual(self.patient.patient_id, "TEST001")
        self.assertEqual(self.patient.allergies, "None known")
    
    def test_patient_validation(self):
        """Test patient data validation."""
        with self.assertRaises(ValidationError):
            PatientDemographics.objects.create(
                patient_id="TEST001"  # Duplicate ID
            )
```

### Form Tests
```python
class VitalsFormTests(TestCase):
    """Tests for vitals form validation."""
    
    def test_blood_pressure_validation(self):
        """Test blood pressure format validation."""
        form_data = {
            'blood_pressure': '120/80',
            'temperature': 98.6,
            'pulse': 72
        }
        form = VitalsForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        form_data['blood_pressure'] = '12080'  # Invalid format
        form = VitalsForm(data=form_data)
        self.assertFalse(form.is_valid())
```

### View Tests
```python
class PatientViewTests(PatientRecordTestCase):
    """Tests for patient views."""
    
    def test_patient_list_view(self):
        """Test patient list display."""
        response = self.client.get(reverse('patient-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TEST001")
    
    def test_patient_detail_view(self):
        """Test patient detail display."""
        response = self.client.get(
            reverse('patient-detail', args=[self.patient.patient_id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.patient.allergies)
```

### API Tests
```python
from rest_framework.test import APITestCase

class PatientAPITests(APITestCase):
    """Tests for patient API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.patient_data = {
            'patient_id': 'TEST002',
            'allergies': 'Penicillin',
            'code_status': 'Full Code'
        }
    
    def test_create_patient(self):
        """Test patient creation via API."""
        response = self.client.post(
            reverse('api-patient-create'),
            self.patient_data,
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            PatientDemographics.objects.count(), 1
        )
```

## Test Data Management

### Fixtures
```yaml
# patient_records/fixtures/test_data.yaml
- model: patient_records.PatientDemographics
  pk: 1
  fields:
    patient_id: TEST001
    allergies: None known
    code_status: Full Code
    date: 2024-01-01

- model: patient_records.Diagnosis
  pk: 1
  fields:
    patient_id: TEST001
    diagnosis: Hypertension
    icd_code: I10
    date: 2024-01-01
```

### Factory Classes
```python
import factory
from datetime import date
from patient_records.models import PatientDemographics

class PatientFactory(factory.django.DjangoModelFactory):
    """Factory for generating test patient data."""
    
    class Meta:
        model = PatientDemographics
    
    patient_id = factory.Sequence(lambda n: f'TEST{n:03d}')
    allergies = factory.Faker('text', max_nb_chars=100)
    code_status = factory.Iterator(['Full Code', 'DNR', 'DNI'])
    date = factory.LazyFunction(date.today)
```

## Integration Tests

### Form Submission Tests
```python
class PatientFormIntegrationTests(TestCase):
    """Integration tests for patient form submission."""
    
    def test_patient_creation_workflow(self):
        """Test complete patient creation workflow."""
        # Create patient demographics
        response = self.client.post(reverse('patient-create'), {
            'patient_id': 'TEST003',
            'allergies': 'None known',
            'code_status': 'Full Code'
        })
        self.assertEqual(response.status_code, 302)
        
        # Add diagnosis
        patient = PatientDemographics.objects.get(patient_id='TEST003')
        response = self.client.post(
            reverse('diagnosis-create', args=[patient.patient_id]),
            {
                'diagnosis': 'Hypertension',
                'icd_code': 'I10'
            }
        )
        self.assertEqual(response.status_code, 302)
```

## Performance Tests

### Query Optimization Tests
```python
class QueryOptimizationTests(TestCase):
    """Tests for query performance optimization."""
    
    def setUp(self):
        """Create test data."""
        PatientFactory.create_batch(100)
    
    def test_patient_list_queries(self):
        """Test number of queries for patient list."""
        with self.assertNumQueries(1):
            response = self.client.get(reverse('patient-list'))
            self.assertEqual(response.status_code, 200)
```

## Test Coverage

### Coverage Configuration
```ini
# .coveragerc
[run]
source = patient_records
omit =
    */migrations/*
    */tests/*
    */admin.py

[report]
exclude_lines =
    pragma: no cover
    def __str__
    if settings.DEBUG
```

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific test file
python manage.py test patient_records.tests.test_models

# Run with coverage
coverage run manage.py test
coverage report
```

## Related Documentation
- [[Development Guide]]
- [[Code Style Guide]]
- [[API Documentation]]

## Tags
#testing #quality-assurance #django #python