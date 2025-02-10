from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Patient, Diagnosis, Vitals, Symptoms, EventStore
from ..event_sourcing.constants import *
from .test_utils import validate_event_store_entry, get_expected_event_data
from unittest.mock import patch
import datetime
import os
from django.conf import settings

@override_settings(
    STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage',
    STATIC_URL='/static/',
    STATIC_ROOT=os.path.join(settings.BASE_DIR, 'static')
)
class FormSubmissionTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Create test patient
        self.patient = Patient.objects.create(
            first_name="Test",
            last_name="Patient",
            date_of_birth=datetime.date(1990, 1, 1),
            gender="M",
            patient_number="TP001"
        )
        self.expected_event_data = get_expected_event_data()

    @patch('patient_records.event_sourcing.event_store.EventStoreService')
    def test_vitals_form_submission(self, mock_event_store):
        """Test successful vitals form submission"""
        url = reverse('add_vitals', args=[self.patient.id])
        data = {
            'date': '2024-03-20',
            'blood_pressure': '120/80',
            'temperature': 98.6,
            'spo2': 98.0,
            'pulse': 72,
            'respirations': 16,
            'supp_o2': False,
            'pain': 2,
            'source': 'Test Source'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        
        # Verify vitals were created
        vitals = Vitals.objects.first()
        self.assertIsNotNone(vitals)
        self.assertEqual(vitals.blood_pressure, '120/80')
        
        # Verify event store entry
        event = EventStore.objects.filter(event_type=VITALS_RECORDED).first()
        self.assertIsNotNone(event)
        
        validation_errors = validate_event_store_entry(
            event,
            self.expected_event_data[VITALS_RECORDED]['aggregate_type'],
            VITALS_RECORDED,
            self.expected_event_data[VITALS_RECORDED]['required_keys']
        )
        self.assertEqual(validation_errors, [])

    @patch('patient_records.event_sourcing.event_store.EventStoreService')
    def test_diagnosis_form_submission(self, mock_event_store):
        """Test successful diagnosis form submission"""
        url = reverse('add_diagnosis', args=[self.patient.id])
        data = {
            'icd_code': 'J45.901',
            'diagnosis': 'Asthma',
            'date': '2024-03-20',
            'notes': 'Test diagnosis notes',
            'source': 'Test Source'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        
        # Verify diagnosis was created
        diagnosis = Diagnosis.objects.first()
        self.assertIsNotNone(diagnosis)
        self.assertEqual(diagnosis.diagnosis, 'Asthma')
        
        # Verify event store entry
        event = EventStore.objects.filter(event_type=DIAGNOSIS_ADDED).first()
        self.assertIsNotNone(event)
        
        validation_errors = validate_event_store_entry(
            event,
            self.expected_event_data[DIAGNOSIS_ADDED]['aggregate_type'],
            DIAGNOSIS_ADDED,
            self.expected_event_data[DIAGNOSIS_ADDED]['required_keys']
        )
        self.assertEqual(validation_errors, [])

    @patch('patient_records.event_sourcing.event_store.EventStoreService')
    def test_symptoms_form_submission(self, mock_event_store):
        """Test successful symptoms form submission"""
        url = reverse('add_symptoms', args=[self.patient.id])
        data = {
            'date': '2024-03-20',
            'symptom': 'Headache',
            'notes': 'Patient reports persistent headache',
            'source': 'Test Source',
            'person_reporting': 'Test Reporter'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        
        # Verify symptoms were created
        symptoms = Symptoms.objects.first()
        self.assertIsNotNone(symptoms)
        self.assertEqual(symptoms.symptom, 'Headache')
        
        # Verify event store entry
        event = EventStore.objects.filter(event_type=SYMPTOMS_ADDED).first()
        self.assertIsNotNone(event)
        
        validation_errors = validate_event_store_entry(
            event,
            self.expected_event_data[SYMPTOMS_ADDED]['aggregate_type'],
            SYMPTOMS_ADDED,
            self.expected_event_data[SYMPTOMS_ADDED]['required_keys']
        )
        self.assertEqual(validation_errors, [])

    @patch('patient_records.event_sourcing.event_store.EventStoreService')
    def test_invalid_vitals_submission(self, mock_event_store):
        """Test invalid vitals form submission"""
        url = reverse('add_vitals', args=[self.patient.id])
        data = {
            'date': '2024-03-20',
            'temperature': 'invalid',
            'pulse': 'invalid',
            'blood_pressure': 'invalid',
            'respirations': 'invalid',
            'spo2': 'invalid',
            'supp_o2': 'invalid',
            'pain': 'invalid',
            'source': ''  # Required field left empty
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)  # Returns to form
        self.assertFalse(Vitals.objects.filter(patient=self.patient).exists())
        mock_event_store.return_value.append_event.assert_not_called()
        
    @patch('patient_records.event_sourcing.event_store.EventStoreService')
    def test_invalid_diagnosis_submission(self, mock_event_store):
        """Test invalid diagnosis form submission"""
        url = reverse('add_diagnosis', args=[self.patient.id])
        data = {
            'diagnosis': '',  # Required field
            'diagnosis_date': 'invalid-date',
            'notes': '',
            'source': ''  # Required field
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Diagnosis.objects.filter(patient=self.patient).exists())
        mock_event_store.return_value.append_event.assert_not_called()
        
    @patch('patient_records.event_sourcing.event_store.EventStoreService')
    def test_invalid_symptoms_submission(self, mock_event_store):
        """Test invalid symptoms form submission"""
        url = reverse('add_symptoms', args=[self.patient.id])
        data = {
            'symptom': '',  # Required field
            'severity': 'invalid',
            'onset_date': 'invalid-date',
            'notes': '',
            'source': ''  # Required field
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Symptoms.objects.filter(patient=self.patient).exists())
        mock_event_store.return_value.append_event.assert_not_called() 