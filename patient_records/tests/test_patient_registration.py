from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Patient, AuditTrail, EventStore
from ..models.audit.constants import PATIENT_AGGREGATE, PATIENT_REGISTERED
from ..forms import PatientForm
import datetime
from django.utils import timezone

class PatientRegistrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Valid patient data for tests
        self.valid_patient_data = {
            'patient_number': 'TEST001',
            'first_name': 'John',
            'last_name': 'Doe',
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'address': '123 Test St',
            'phone': '555-555-5555',
            'email': 'john@example.com',
            'emergency_contact': 'Jane Doe - 555-555-5556',
            'insurance_info': 'Test Insurance'
        }

    def test_patient_form_valid(self):
        """Test that PatientForm validates with correct data"""
        form = PatientForm(data=self.valid_patient_data)
        self.assertTrue(form.is_valid())

    def test_patient_form_invalid(self):
        """Test that PatientForm invalidates with incorrect data"""
        invalid_data = self.valid_patient_data.copy()
        invalid_data['date_of_birth'] = 'invalid-date'
        form = PatientForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('date_of_birth', form.errors)

    def test_patient_registration_view(self):
        """Test the patient registration view with valid data"""
        response = self.client.post(
            reverse('add_patient'),
            data=self.valid_patient_data
        )
        self.assertEqual(Patient.objects.count(), 1)
        patient = Patient.objects.first()
        self.assertEqual(patient.patient_number, 'TEST001')
        self.assertEqual(patient.first_name, 'John')
        self.assertEqual(patient.last_name, 'Doe')

    def test_patient_registration_creates_audit_trail(self):
        """Test that patient registration creates an audit trail entry"""
        response = self.client.post(
            reverse('add_patient'),
            data=self.valid_patient_data
        )
        self.assertEqual(AuditTrail.objects.count(), 1)
        audit = AuditTrail.objects.first()
        self.assertEqual(audit.action, 'CREATE')
        self.assertEqual(audit.record_type, 'PATIENT')

    def test_duplicate_patient_number(self):
        """Test that duplicate patient numbers are not allowed"""
        # Create first patient
        Patient.objects.create(
            patient_number='TEST001',
            first_name='Jane',
            last_name='Smith',
            date_of_birth=datetime.date(1990, 1, 1),
            gender='F',
            address='456 Test Ave',
            phone='555-555-5557'
        )
        
        # Try to create second patient with same number
        response = self.client.post(
            reverse('add_patient'),
            data=self.valid_patient_data
        )
        self.assertEqual(Patient.objects.count(), 1)  # Should still be just one
        self.assertContains(response, 'patient number', status_code=200)

    def test_required_fields(self):
        """Test that required fields are enforced"""
        required_fields = [
            'patient_number',
            'first_name',
            'last_name',
            'date_of_birth',
            'gender',
            'address',
            'phone'
        ]
        
        for field in required_fields:
            invalid_data = self.valid_patient_data.copy()
            del invalid_data[field]
            form = PatientForm(data=invalid_data)
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)

    def test_future_date_of_birth(self):
        """Test that future dates are not allowed for date_of_birth"""
        invalid_data = self.valid_patient_data.copy()
        future_date = (timezone.now().date() + datetime.timedelta(days=1)).isoformat()
        invalid_data['date_of_birth'] = future_date
        form = PatientForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('date_of_birth', form.errors)
        self.assertEqual(form.errors['date_of_birth'][0], 'Future dates are not allowed.')

    def test_immutable_patient_number(self):
        """Test that patient number cannot be changed after creation."""
        # Create initial patient
        response = self.client.post(
            reverse('add_patient'),
            data=self.valid_patient_data
        )
        patient = Patient.objects.first()
        
        # Try to update patient number
        modified_data = self.valid_patient_data.copy()
        modified_data['patient_number'] = 'TEST002'
        form = PatientForm(data=modified_data, instance=patient)
        self.assertFalse(form.is_valid())
        self.assertIn('patient_number', form.errors)
        self.assertIn('cannot be changed', str(form.errors['patient_number']))

    def test_immutable_date_of_birth(self):
        """Test that date of birth cannot be changed after creation."""
        # Create initial patient
        response = self.client.post(
            reverse('add_patient'),
            data=self.valid_patient_data
        )
        patient = Patient.objects.first()
        
        # Try to update date of birth
        modified_data = self.valid_patient_data.copy()
        modified_data['date_of_birth'] = '1991-01-01'
        form = PatientForm(data=modified_data, instance=patient)
        self.assertFalse(form.is_valid())
        self.assertIn('date_of_birth', form.errors)
        self.assertIn('cannot be changed', str(form.errors['date_of_birth']))

    def test_event_creation(self):
        """Test that patient registration creates appropriate events."""
        response = self.client.post(
            reverse('add_patient'),
            data=self.valid_patient_data
        )
        patient = Patient.objects.first()
        
        # Verify event was created
        events = EventStore.objects.filter(
            aggregate_type=PATIENT_AGGREGATE,
            aggregate_id=str(patient.id)
        )
        self.assertEqual(events.count(), 1)
        
        event = events.first()
        self.assertEqual(event.event_type, PATIENT_REGISTERED)
        self.assertEqual(event.sequence, 1)
        self.assertEqual(event.event_data['patient_number'], 'TEST001')
        self.assertEqual(event.event_data['date_of_birth'], '1990-01-01') 