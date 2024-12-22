# How to Contribute

## Overview
This guide outlines the process for contributing to the Patient Management System, including coding standards, pull request procedures, and best practices.

## Getting Started

### Development Environment
1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/patient_input_app.git
   cd patient_input_app
   ```
3. Set up development environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Branch Naming Convention
- Feature branches: `feature/description`
- Bug fixes: `bugfix/description`
- Documentation: `docs/description`
- Performance improvements: `perf/description`

## Code Standards

### Python Style Guide
- Follow PEP 8 guidelines
- Use Black for code formatting
- Maximum line length: 88 characters
- Use type hints for function parameters and returns

Example:
```python
from typing import List, Optional

def process_patient_data(
    patient_id: str,
    records: List[dict],
    update_existing: bool = False
) -> Optional[dict]:
    """
    Process patient medical records.
    
    Args:
        patient_id: Unique identifier for the patient
        records: List of medical record dictionaries
        update_existing: Whether to update existing records
        
    Returns:
        Processed patient data or None if patient not found
    """
    pass
```

### JavaScript Style Guide
- Use ES6+ features
- Follow Airbnb JavaScript Style Guide
- Use async/await for asynchronous operations
- Implement proper error handling

Example:
```javascript
async function fetchPatientData(patientId) {
    try {
        const response = await fetch(`/api/patients/${patientId}/`);
        if (!response.ok) {
            throw new Error('Failed to fetch patient data');
        }
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}
```

## Testing Requirements

### Unit Tests
- Write tests for all new features
- Maintain minimum 80% code coverage
- Use pytest for Python tests
- Use Jest for JavaScript tests

Example:
```python
import pytest
from patient_records.models import Patient

@pytest.mark.django_db
class TestPatientModel:
    def test_patient_creation(self):
        patient = Patient.objects.create(
            patient_id="TEST001",
            first_name="John",
            last_name="Doe"
        )
        assert patient.patient_id == "TEST001"
        assert str(patient) == "John Doe"
```

### Integration Tests
- Test API endpoints
- Test database interactions
- Test third-party integrations

Example:
```python
from rest_framework.test import APITestCase

class TestPatientAPI(APITestCase):
    def test_create_patient(self):
        data = {
            "patient_id": "TEST002",
            "first_name": "Jane",
            "last_name": "Doe"
        }
        response = self.client.post('/api/patients/', data)
        self.assertEqual(response.status_code, 201)
```

## Documentation

### Code Documentation
- Add docstrings to all functions and classes
- Include type hints
- Document exceptions and edge cases
- Provide usage examples

Example:
```python
class PatientRecord:
    """
    Manages patient medical records.
    
    Attributes:
        patient_id (str): Unique patient identifier
        records (List[dict]): List of medical records
        
    Raises:
        ValueError: If patient_id is invalid
        DatabaseError: If database connection fails
    """
    pass
```

### API Documentation
- Document all API endpoints
- Include request/response examples
- Specify authentication requirements
- List possible error responses

Example:
```yaml
/api/patients/{patient_id}:
  get:
    summary: Retrieve patient information
    parameters:
      - name: patient_id
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Patient data retrieved successfully
      404:
        description: Patient not found
```

## Pull Request Process

### Before Submitting
1. Run all tests
2. Update documentation
3. Format code using Black
4. Check for security vulnerabilities
5. Update requirements.txt if needed

### PR Template
```markdown
## Description
[Description of changes]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests passing

## Documentation
- [ ] Code documentation updated
- [ ] API documentation updated
- [ ] README updated if needed

## Security
- [ ] Security implications considered
- [ ] No sensitive data exposed
```

## Code Review Guidelines

### Reviewer Checklist
1. Code quality and style
2. Test coverage
3. Documentation completeness
4. Security considerations
5. Performance implications
6. Error handling
7. Edge cases considered

### Review Comments
- Be constructive and specific
- Provide examples when suggesting changes
- Reference documentation or best practices
- Consider alternative approaches

## Related Documentation
- [[Development Guide]]
- [[Code Style Guide]]
- [[Testing Guidelines]]
- [[Security Implementation]]

## Tags
#contributing #development #guidelines #best-practices 