# Code Style Guide

## Overview
This document outlines the coding standards and style guidelines for the Patient Input Application, ensuring consistent code quality across the project.

## Python Style Guidelines

### Code Formatting
We use Black for code formatting with the following configuration:
```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
```

### Import Organization
```python
# First: Standard library imports
from datetime import date, datetime
from typing import List, Optional

# Second: Third-party imports
from django.db import models
from django.core.validators import RegexValidator

# Third: Local application imports
from patient_records.models import Patient
from .utils import calculate_age

# Wrong:
from .models import * # Avoid wildcard imports
```

### Model Definitions
```python
class PatientDemographics(models.Model):
    """
    Patient demographics information.
    
    This model stores basic patient information including contact details
    and demographic data required for patient management.
    """
    patient_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique patient identifier"
    )
    date = models.DateField(
        auto_now_add=True,
        help_text="Record creation date"
    )
    allergies = models.TextField(
        blank=True,
        help_text="Patient allergies and reactions"
    )
    code_status = models.CharField(
        max_length=50,
        help_text="Patient's current code status"
    )
    
    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['patient_id']),
            models.Index(fields=['date'])
        ]
```

### View Organization
```python
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

class PatientListView(LoginRequiredMixin, ListView):
    """Display list of patients with filtering capabilities."""
    model = Patient
    template_name = 'patient_records/list.html'
    context_object_name = 'patients'
    paginate_by = 25
    
    def get_queryset(self):
        """
        Filter patients based on search criteria.
        
        Returns:
            QuerySet: Filtered patient queryset
        """
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(patient_id__icontains=search_query) |
                Q(demographics__allergies__icontains=search_query)
            )
        return queryset
```

### Form Validation
```python
class PatientForm(forms.ModelForm):
    """Form for creating and updating patient records."""
    
    patient_phone = forms.CharField(
        validators=[
            RegexValidator(
                regex=r'^\(\d{3}\) \d{3}-\d{4}$',
                message="Phone must be in format (XXX) XXX-XXXX"
            )
        ]
    )
    
    def clean_date(self):
        """Validate date is not in future."""
        date = self.cleaned_data['date']
        if date > datetime.now().date():
            raise ValidationError("Date cannot be in the future")
        return date
```

### JavaScript Style

#### Event Handlers
```javascript
// Good: Use event delegation
document.querySelector('.tab-container').addEventListener('click', (e) => {
    if (e.target.matches('.tab')) {
        loadTabContent(e.target.dataset.tab);
    }
});

// Bad: Attaching handlers to multiple elements
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', handleClick);
});
```

#### API Calls
```javascript
// Good: Async/await with error handling
async function loadPatientData(patientId) {
    try {
        const response = await fetch(`/api/patients/${patientId}/`);
        if (!response.ok) throw new Error('Failed to load patient data');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error loading patient data:', error);
        showErrorMessage('Failed to load patient data');
    }
}
```

### Template Organization

#### Base Template Structure
```html
{% extends "base.html" %}

{% block title %}Patient Records - {{ patient.id }}{% endblock %}

{% block content %}
<div class="patient-container">
    {% include "patient_records/partials/patient_header.html" %}
    
    <div class="tab-container" data-patient-id="{{ patient.id }}">
        {% include "patient_records/partials/tabs.html" %}
        
        <div class="tab-content">
            {% block tab_content %}{% endblock %}
        </div>
    </div>
</div>
{% endblock %}
```

### Error Handling

#### Python Exceptions
```python
class PatientNotFoundError(Exception):
    """Raised when a patient record cannot be found."""
    pass

def get_patient_record(patient_id):
    """
    Retrieve patient record by ID.
    
    Args:
        patient_id (str): Patient's unique identifier
        
    Returns:
        Patient: Patient record
        
    Raises:
        PatientNotFoundError: If patient record doesn't exist
    """
    try:
        return Patient.objects.get(patient_id=patient_id)
    except Patient.DoesNotExist:
        raise PatientNotFoundError(f"Patient {patient_id} not found")
```

### Documentation Standards

#### Function Docstrings
```python
def calculate_bmi(weight: float, height: float) -> float:
    """
    Calculate Body Mass Index (BMI).
    
    Args:
        weight (float): Patient's weight in kilograms
        height (float): Patient's height in meters
        
    Returns:
        float: Calculated BMI value
        
    Raises:
        ValueError: If weight or height is negative or zero
    """
    if weight <= 0 or height <= 0:
        raise ValueError("Weight and height must be positive values")
    return weight / (height ** 2)
```

### Testing Standards

#### Test Organization
```python
class PatientRecordTests(TestCase):
    """Tests for patient record functionality."""
    
    def setUp(self):
        """Create test data."""
        self.patient = Patient.objects.create(
            patient_id="TEST001",
            date=date.today()
        )
    
    def test_patient_creation(self):
        """Test patient record creation."""
        self.assertEqual(self.patient.patient_id, "TEST001")
        self.assertEqual(self.patient.date, date.today())
```

## Related Documentation
- [[Development Guide]]
- [[Testing Guidelines]]
- [[API Documentation]]

## Tags
#coding-standards #style-guide #python #javascript