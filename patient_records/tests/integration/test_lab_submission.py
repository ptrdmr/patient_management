"""Integration tests for lab result submission functionality."""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ...models import Patient, CmpLabs, CbcLabs, AuditTrail
from django.core.cache import cache
import json
from datetime import datetime, date

class LabResultSubmissionTests(TestCase):
    """Test suite for lab result submission functionality."""

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
        # Create test patient
        self.patient = Patient.objects.create(
            first_name='John',
            last_name='Doe',
            date_of_birth=date(1990, 1, 1),
            gender='M',
            patient_number='TEST001',
            email='john.doe@example.com',
            phone='555-0123',
            address='123 Test St, Test City, TS 12345',
            emergency_contact='Jane Doe, 555-0124',
            insurance_info='Test Insurance Co, Policy #12345'
        )
        self.client.login(username='testuser', password='testpass123')
        cache.clear()

    def tearDown(self):
        """Clean up after tests."""
        cache.clear()

    def test_cmp_lab_submission(self):
        """Test submission of CMP lab results."""
        # 1. Get the CMP lab form
        response = self.client.get(reverse('add_cmp_labs', args=[self.patient.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'patient_records/add_cmp_labs.html')

        # 2. Submit CMP lab results
        cmp_data = {
            'date': '2024-01-15',
            'sodium': 140,
            'potassium': 4.0,
            'chloride': 100,
            'co2': 24,
            'bun': 15,
            'creatinine': 1.0,
            'glucose': 100,
            'calcium': 9.5,
            'protein': 7.0,
            'albumin': 4.0,
            'bilirubin': 1.0,
            'gfr': 60
        }

        response = self.client.post(
            reverse('add_cmp_labs', args=[self.patient.id]),
            cmp_data,
            follow=True
        )

        # 3. Verify submission
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            reverse('patient_detail', args=[self.patient.id])
        )

        # 4. Verify lab results were created
        cmp_lab = CmpLabs.objects.first()
        self.assertIsNotNone(cmp_lab)
        self.assertEqual(cmp_lab.sodium, 140)
        self.assertEqual(cmp_lab.glucose, 100)

        # 5. Verify audit trail
        audit = AuditTrail.objects.first()
        self.assertIsNotNone(audit)
        self.assertEqual(audit.action, 'CREATE')
        self.assertEqual(audit.record_type, 'CMP_LAB')
        self.assertEqual(audit.user, self.user)

    def test_cbc_lab_submission(self):
        """Test submission of CBC lab results."""
        # 1. Get the CBC lab form
        response = self.client.get(reverse('add_cbc_labs', args=[self.patient.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'patient_records/add_cbc_labs.html')

        # 2. Submit CBC lab results
        cbc_data = {
            'date': '2024-01-15',
            'wbc': 7.5,
            'rbc': 4.5,
            'hemoglobin': 14.0,
            'hematocrit': 42.0,
            'mcv': 90.0,
            'mch': 30.0,
            'mchc': 33.0,
            'rdw': 13.0,
            'platelets': 250.0,
            'neutrophils': 60.0,
            'lymphocytes': 30.0,
            'monocytes': 7.0,
            'eosinophils': 2.0,
            'basophils': 1.0
        }

        response = self.client.post(
            reverse('add_cbc_labs', args=[self.patient.id]),
            cbc_data,
            follow=True
        )

        # 3. Verify submission
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            reverse('patient_detail', args=[self.patient.id])
        )

        # 4. Verify lab results were created
        cbc_lab = CbcLabs.objects.first()
        self.assertIsNotNone(cbc_lab)
        self.assertEqual(cbc_lab.wbc, 7.5)
        self.assertEqual(cbc_lab.hemoglobin, 14.0)

        # 5. Verify audit trail
        audit = AuditTrail.objects.first()
        self.assertIsNotNone(audit)
        self.assertEqual(audit.action, 'CREATE')
        self.assertEqual(audit.record_type, 'CBC_LAB')
        self.assertEqual(audit.user, self.user)

    def test_invalid_cmp_submission(self):
        """Test submission of invalid CMP lab data."""
        invalid_data = {
            'date': 'invalid-date',
            'sodium': 'not-a-number',
            'glucose': -1  # Invalid negative value
        }

        response = self.client.post(
            reverse('add_cmp_labs', args=[self.patient.id]),
            invalid_data
        )

        self.assertEqual(response.status_code, 200)  # Returns to form
        self.assertFalse(CmpLabs.objects.exists())
        self.assertFormError(response, 'cmp_form', 'date', 'Enter a valid date.')
        self.assertFormError(response, 'cmp_form', 'sodium', 'Enter a number.')

    def test_invalid_cbc_submission(self):
        """Test submission of invalid CBC lab data."""
        invalid_data = {
            'date': 'invalid-date',
            'wbc': 'not-a-number',
            'hemoglobin': -1  # Invalid negative value
        }

        response = self.client.post(
            reverse('add_cbc_labs', args=[self.patient.id]),
            invalid_data
        )

        self.assertEqual(response.status_code, 200)  # Returns to form
        self.assertFalse(CbcLabs.objects.exists())
        self.assertFormError(response, 'cbc_form', 'date', 'Enter a valid date.')
        self.assertFormError(response, 'cbc_form', 'wbc', 'Enter a number.')

    def test_unauthorized_lab_submission(self):
        """Test lab submission by unauthorized user."""
        self.client.logout()
        
        cmp_data = {
            'date': '2024-01-15',
            'sodium': 140,
            'glucose': 100
        }

        # Try to submit CMP labs
        response = self.client.post(
            reverse('add_cmp_labs', args=[self.patient.id]),
            cmp_data
        )
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('add_cmp_labs', args=[self.patient.id])}")
        self.assertFalse(CmpLabs.objects.exists())

        # Try to submit CBC labs
        cbc_data = {
            'date': '2024-01-15',
            'wbc': 7.5,
            'hemoglobin': 14.0
        }

        response = self.client.post(
            reverse('add_cbc_labs', args=[self.patient.id]),
            cbc_data
        )
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('add_cbc_labs', args=[self.patient.id])}")
        self.assertFalse(CbcLabs.objects.exists()) 