"""Integration tests for medication management functionality."""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ...models import Patient, Medications, AuditTrail
from django.core.cache import cache
import json
from datetime import date, timedelta

class MedicationManagementTests(TestCase):
    """Test suite for medication management functionality."""

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

    def test_add_basic_medication(self):
        """Test adding a basic medication."""
        med_data = {
            'date_prescribed': date.today().isoformat(),
            'drug': 'Ibuprofen',
            'dose': '400mg',
            'route': 'Oral',
            'frequency': 'Every 6 hours',
            'prn': True,
            'notes': 'Take with food'
        }

        response = self.client.post(
            reverse('add_medications', args=[self.patient.id]),
            med_data,
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            reverse('patient_detail', args=[self.patient.id])
        )

        # Verify medication was created
        med = Medications.objects.first()
        self.assertIsNotNone(med)
        self.assertEqual(med.drug, 'Ibuprofen')
        self.assertEqual(med.dose, '400mg')
        self.assertEqual(med.route, 'Oral')
        self.assertTrue(med.prn)
        self.assertIsNone(med.dc_date)

    def test_add_medication_with_discontinue_date(self):
        """Test adding a medication with a discontinue date."""
        future_date = date.today() + timedelta(days=30)
        med_data = {
            'date_prescribed': date.today().isoformat(),
            'drug': 'Amoxicillin',
            'dose': '500mg',
            'route': 'Oral',
            'frequency': 'Three times daily',
            'prn': False,
            'dc_date': future_date.isoformat(),
            'notes': '10-day course'
        }

        response = self.client.post(
            reverse('add_medications', args=[self.patient.id]),
            med_data,
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        
        # Verify medication was created with discontinue date
        med = Medications.objects.first()
        self.assertIsNotNone(med)
        self.assertEqual(med.drug, 'Amoxicillin')
        self.assertEqual(med.dc_date, future_date)
        self.assertFalse(med.prn)

    def test_current_medications_filter(self):
        """Test filtering of current medications."""
        # Create active medication
        active_med = Medications.objects.create(
            patient=self.patient,
            date_prescribed=date.today(),
            drug='Active Med',
            dose='100mg',
            route='Oral',
            frequency='Daily'
        )

        # Create discontinued medication
        discontinued_med = Medications.objects.create(
            patient=self.patient,
            date_prescribed=date.today() - timedelta(days=30),
            drug='Old Med',
            dose='200mg',
            route='Oral',
            frequency='Daily',
            dc_date=date.today() - timedelta(days=1)
        )

        # Get current medications
        current_meds = Medications.objects.filter(
            patient=self.patient,
            dc_date__isnull=True
        )

        self.assertEqual(current_meds.count(), 1)
        self.assertEqual(current_meds.first().drug, 'Active Med')

    def test_invalid_medication_data(self):
        """Test adding medication with invalid data."""
        invalid_data = {
            'date_prescribed': date.today().isoformat(),  # Valid date
            'drug': '',  # Required field
            'dose': '',  # Required field
            'route': '',  # Required field
            'frequency': ''  # Required field
        }

        response = self.client.post(
            reverse('add_medications', args=[self.patient.id]),
            invalid_data
        )

        self.assertEqual(response.status_code, 200)  # Returns to form
        self.assertFalse(Medications.objects.exists())
        self.assertIn('drug', response.context['form'].errors)
        self.assertIn('This field is required.', response.context['form'].errors['drug'])

    def test_unauthorized_medication_access(self):
        """Test medication management by unauthorized user."""
        self.client.logout()
        
        med_data = {
            'date_prescribed': date.today().isoformat(),
            'drug': 'Test Drug',
            'dose': '100mg',
            'route': 'Oral',
            'frequency': 'Daily'
        }

        response = self.client.post(
            reverse('add_medications', args=[self.patient.id]),
            med_data
        )

        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertFalse(Medications.objects.exists())

    def test_invalid_discontinue_date(self):
        """Test adding medication with invalid discontinue date."""
        past_date = date.today() - timedelta(days=1)
        med_data = {
            'date_prescribed': date.today().isoformat(),
            'drug': 'Test Drug',
            'dose': '100mg',
            'route': 'Oral',
            'frequency': 'Daily',
            'dc_date': past_date.isoformat()  # Discontinue date before prescribed date
        }

        response = self.client.post(
            reverse('add_medications', args=[self.patient.id]),
            med_data
        )

        self.assertEqual(response.status_code, 200)  # Returns to form
        self.assertFalse(Medications.objects.exists())

    def test_multiple_active_medications(self):
        """Test handling of multiple active medications."""
        # Create multiple medications in reverse order
        meds_data = [
            {
                'date_prescribed': (date.today() - timedelta(days=i)).isoformat(),
                'drug': f'Drug {i+1}',
                'dose': f'{i+1}00mg',
                'route': 'Oral',
                'frequency': 'Daily'
            } for i in range(2, -1, -1)  # This will create dates from oldest to newest
        ]

        for med_data in meds_data:
            response = self.client.post(
                reverse('add_medications', args=[self.patient.id]),
                med_data,
                follow=True
            )
            self.assertEqual(response.status_code, 200)

        # Verify all medications were created
        self.assertEqual(Medications.objects.count(), 3)
        
        # Verify medications are listed in correct order (newest first)
        meds = Medications.objects.filter(patient=self.patient).order_by('-date_prescribed')
        self.assertEqual(meds[0].drug, 'Drug 1')  # Most recent
        self.assertEqual(meds[1].drug, 'Drug 2')
        self.assertEqual(meds[2].drug, 'Drug 3')  # Oldest 