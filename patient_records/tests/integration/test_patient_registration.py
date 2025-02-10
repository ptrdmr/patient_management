"""Integration tests for patient registration flow."""

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from ...models import Patient, AuditTrail
from django.core.cache import cache
import json
from datetime import datetime

@override_settings(
    STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage',
    DEBUG_TOOLBAR_CONFIG={'SHOW_TOOLBAR_CALLBACK': lambda request: False}
)
class PatientRegistrationFlowTests(TestCase):
    """Test the complete patient registration flow."""

    def setUp(self):
        """Set up test environment."""
        self.client = Client()
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        self.client.login(username='testuser', password='testpass123')
        # Clear cache
        cache.clear()
        # Common test data
        self.test_date = datetime(1990, 1, 1)

    def tearDown(self):
        """Clean up after tests."""
        cache.clear()

    def test_complete_registration_flow(self):
        """Test the complete patient registration process."""
        # 1. Get the registration form
        response = self.client.get(reverse('add_patient'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'patient_records/add_patient.html')

        # 2. Submit patient registration
        patient_data = {
            'first_name': 'John',
            'middle_name': 'Robert',
            'last_name': 'Doe',
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'patient_number': 'TEST001',
            'email': 'john.doe@example.com',
            'phone': '555-0123',
            'address': '123 Test St',
            'city': 'Test City',
            'state': 'TS',
            'zip_code': '12345',
            'emergency_contact': 'Jane Doe, 555-0124',
            'insurance_info': 'Test Insurance Co, Policy #12345'
        }

        response = self.client.post(
            reverse('add_patient'),
            patient_data,
            follow=True
        )
        
        # 3. Verify redirect to patient detail
        self.assertEqual(response.status_code, 200)
        patient = Patient.objects.first()
        self.assertIsNotNone(patient)
        self.assertRedirects(
            response,
            reverse('patient_detail', args=[patient.id]),
            status_code=302,
            target_status_code=200
        )

        # 4. Verify patient was created
        self.assertEqual(patient.first_name, 'John')
        self.assertEqual(patient.last_name, 'Doe')
        self.assertEqual(patient.patient_number, 'TEST001')

        # 5. Verify audit trail was created
        audit = AuditTrail.objects.first()
        self.assertIsNotNone(audit)
        self.assertEqual(audit.action, 'CREATE')
        self.assertEqual(audit.record_type, 'PATIENT')
        self.assertEqual(audit.user, self.user)

    def test_duplicate_patient_number(self):
        """Test registration with duplicate patient number."""
        # Create initial patient
        Patient.objects.create(
            first_name='Jane',
            last_name='Smith',
            date_of_birth=self.test_date,
            gender='F',
            patient_number='TEST001',
            address='123 Test St',
            phone='555-0123',
            emergency_contact='John Smith, 555-0124',
            insurance_info='Test Insurance'
        )

        # Try to create another patient with same number
        patient_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'patient_number': 'TEST001',  # Same number
            'address': '456 Test St',
            'phone': '555-0125',
            'emergency_contact': 'Jane Doe, 555-0126',
            'insurance_info': 'Test Insurance'
        }

        response = self.client.post(reverse('add_patient'), patient_data)
        self.assertEqual(response.status_code, 200)  # Returns to form
        self.assertFormError(
            response,
            'form',
            'patient_number',
            'Patient with this Patient number already exists.'
        )

    def test_invalid_registration_data(self):
        """Test registration with invalid data."""
        invalid_data = {
            'first_name': '',  # Required field
            'last_name': '',   # Required field
            'date_of_birth': 'invalid-date',
            'gender': 'X',     # Invalid choice
            'patient_number': ''  # Required field
        }

        response = self.client.post(reverse('add_patient'), invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Patient.objects.exists())

        # Verify specific error messages
        self.assertFormError(response, 'form', 'first_name', 'This field is required.')
        self.assertFormError(response, 'form', 'last_name', 'This field is required.')
        self.assertFormError(response, 'form', 'patient_number', 'This field is required.')
        self.assertFormError(response, 'form', 'date_of_birth', 'Enter a valid date.')
        self.assertFormError(response, 'form', 'gender', 'Select a valid choice. X is not one of the available choices.')

    def test_ajax_registration(self):
        """Test patient registration via AJAX."""
        patient_data = {
            'first_name': 'John',
            'middle_name': 'Robert',
            'last_name': 'Doe',
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'patient_number': 'TEST001',
            'email': 'john.doe@example.com',
            'phone': '555-0123',
            'address': '123 Test St',
            'city': 'Test City',
            'state': 'TS',
            'zip_code': '12345',
            'emergency_contact': 'Jane Doe, 555-0124',
            'insurance_info': 'Test Insurance Co, Policy #12345'
        }

        response = self.client.post(
            reverse('add_patient'),
            patient_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertTrue('redirect_url' in data)
        self.assertTrue('message' in data)
        self.assertEqual(data['message'], 'Patient added successfully!')

        # Verify patient was created
        patient = Patient.objects.first()
        self.assertIsNotNone(patient)
        self.assertEqual(patient.first_name, 'John')
        self.assertEqual(patient.last_name, 'Doe')
        self.assertEqual(patient.patient_number, 'TEST001') 