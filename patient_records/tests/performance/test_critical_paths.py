"""Performance tests for critical application paths."""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.test.utils import override_settings
from django.core.cache import cache
from ...models import (
    Patient, Vitals, CmpLabs, CbcLabs, Medications,
    PatientNote, Diagnosis, Visits, Provider
)
from datetime import date, timedelta, timezone
import time
import random
import uuid
from django.utils import timezone

class PerformanceTests(TestCase):
    """Test suite for performance critical paths."""

    @classmethod
    def setUpTestData(cls):
        """Set up data for all test methods."""
        # Create test user
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

        # Create test provider
        cls.provider = Provider.objects.create(
            provider='Test Provider',
            practice='Test Practice',
            address='123 Medical St',
            city='Test City',
            state='TS',
            zip_code='12345',
            phone='123-456-7890'
        )

        # Create test patients (100 patients)
        cls.patients = []
        for i in range(100):
            patient = Patient.objects.create(
                first_name=f'Test{i}',
                last_name=f'Patient{i}',
                date_of_birth=date(1990, 1, 1),
                gender='M',
                patient_number=f'TEST{i:03d}',
                email=f'patient{i}@test.com',
                phone='555-0123',
                address='123 Test St',
                emergency_contact='Emergency Contact',
                insurance_info='Test Insurance'
            )
            cls.patients.append(patient)

        # Create test data for first 10 patients
        for patient in cls.patients[:10]:
            # Create vitals (30 records each)
            for j in range(30):
                Vitals.objects.create(
                    patient=patient,
                    date=date.today() - timedelta(days=j),
                    blood_pressure='120/80',
                    temperature=98.6,
                    spo2=98,
                    pulse=72,
                    respirations=16,
                    pain=0,
                    source='test'
                )

            # Create lab results (20 records each)
            for j in range(20):
                CmpLabs.objects.create(
                    patient=patient,
                    date=date.today() - timedelta(days=j),
                    sodium=140,
                    potassium=4.0,
                    chloride=100,
                    co2=24,
                    glucose=100,
                    bun=15,
                    creatinine=1.0,
                    calcium=9.5,
                    protein=7.0,
                    albumin=4.0,
                    bilirubin=1.0,
                    gfr=60
                )
                CbcLabs.objects.create(
                    patient=patient,
                    date=date.today() - timedelta(days=j),
                    wbc=7.5,
                    rbc=4.5,
                    hemoglobin=14.0,
                    hematocrit=42.0,
                    mcv=90.0,
                    mch=30.0,
                    mchc=33.0,
                    rdw=13.0,
                    platelets=250.0,
                    neutrophils=60.0,
                    lymphocytes=30.0,
                    monocytes=7.0,
                    eosinophils=2.0,
                    basophils=1.0
                )

            # Create medications (10 records each)
            for j in range(10):
                Medications.objects.create(
                    patient=patient,
                    date_prescribed=date.today() - timedelta(days=j*30),
                    drug=f'TestDrug{j}',
                    dose='100mg',
                    frequency='daily',
                    route='oral'
                )

            # Create notes (15 records each)
            for j in range(15):
                PatientNote.objects.create(
                    patient=patient,
                    title=f'Test Note {j}',
                    content=f'Test content for note {j}',
                    category='GENERAL',
                    created_by=cls.user
                )

            # Create diagnoses (5 records each)
            for j in range(5):
                Diagnosis.objects.create(
                    patient=patient,
                    icd_code=f'A{j:02d}',
                    diagnosis=f'Test Diagnosis {j}',
                    date=date.today() - timedelta(days=j*30),
                    provider=cls.provider
                )

            # Create visits (8 records each)
            for j in range(8):
                Visits.objects.create(
                    patient=patient,
                    date=date.today() - timedelta(days=j*30),
                    visit_type='Office Visit',
                    provider=cls.provider,
                    practice='Test Practice',
                    source='test'
                )

    def setUp(self):
        """Set up test data."""
        # Create a unique prefix for this test instance
        self.test_prefix = uuid.uuid4().hex[:6].upper()
        
        # Create test user with a unique username
        username = f'testuser_{uuid.uuid4().hex[:8]}'
        self.user = User.objects.create_user(
            username=username,
            password='testpass123'
        )
        
        # Ensure user is logged in
        login_successful = self.client.login(username=username, password='testpass123')
        self.assertTrue(login_successful, "Failed to log in test user")
        
        # Create test provider
        self.provider = Provider.objects.create(
            provider='Test Provider',
            practice='Test Practice',
            address='123 Test St',
            city='Test City',
            state='TX',
            zip_code='12345',
            phone='123-456-7890'
        )
        
        # Create test patients with unique patient numbers
        self.patients = []
        for i in range(100):
            patient = Patient.objects.create(
                first_name=f'Test{i}',
                last_name=f'Patient{i}',
                date_of_birth=date(1980, 1, 1),
                gender='M',
                patient_number=f'{self.test_prefix}{i:03d}',
                address='123 Test St',
                phone='555-0123',
                emergency_contact='Emergency Contact',
                insurance_info='Test Insurance'
            )
            self.patients.append(patient)
        
        # Create test data for first 10 patients
        for patient in self.patients[:10]:
            # Create vitals
            for _ in range(30):
                Vitals.objects.create(
                    patient=patient,
                    date=timezone.now(),
                    blood_pressure='120/80',
                    temperature=98.6,
                    pulse=72,
                    respirations=16,
                    spo2=98,
                    pain=0,
                    source='test'
                )
            
            # Create lab results
            for _ in range(20):
                CmpLabs.objects.create(
                    patient=patient,
                    date=timezone.now(),
                    sodium=140,
                    potassium=4.0,
                    chloride=100,
                    co2=24,
                    glucose=100,
                    bun=15,
                    creatinine=1.0,
                    calcium=9.5,
                    protein=7.0,
                    albumin=4.0,
                    bilirubin=1.0,
                    gfr=60
                )
            
            # Create medications
            for _ in range(10):
                Medications.objects.create(
                    patient=patient,
                    date_prescribed=timezone.now(),
                    drug=f'TestDrug{_}',
                    dose='10mg',
                    frequency='Daily',
                    route='oral'
                )
            
            # Create notes
            for _ in range(15):
                PatientNote.objects.create(
                    patient=patient,
                    title=f'Test Note {_}',
                    content=f'Test content for note {_}',
                    category='GENERAL',
                    created_by=self.user
                )
            
            # Create diagnoses
            for _ in range(5):
                Diagnosis.objects.create(
                    patient=patient,
                    date=timezone.now(),
                    icd_code=f'A{_:02d}',
                    diagnosis=f'Test Diagnosis {_}',
                    provider=self.provider
                )
            
            # Create visits
            for _ in range(8):
                Visits.objects.create(
                    patient=patient,
                    date=timezone.now(),
                    visit_type='Office Visit',
                    provider=self.provider,
                    practice='Test Practice',
                    source='test'
                )

        cache.clear()

    def tearDown(self):
        """Clean up after each test method."""
        cache.clear()

    def test_patient_list_performance(self):
        """Test performance of patient list view."""
        start_time = time.time()
        response = self.client.get(reverse('patient_list'))
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        load_time = end_time - start_time
        self.assertLess(load_time, 1.0)  # Should load in under 1 second

    def test_patient_detail_performance(self):
        """Test performance of patient detail view."""
        # Test with a patient that has full data
        patient = self.patients[0]
        
        start_time = time.time()
        response = self.client.get(reverse('patient_detail', args=[patient.id]))
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        load_time = end_time - start_time
        self.assertLess(load_time, 1.0)  # Should load in under 1 second

    def test_dashboard_performance(self):
        """Test performance of dashboard view."""
        start_time = time.time()
        response = self.client.get(reverse('overview_dashboard'))
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        load_time = end_time - start_time
        self.assertLess(load_time, 2.0)  # Should load in under 2 seconds

    def test_patient_search_performance(self):
        """Test performance of patient search."""
        # Test different search scenarios
        search_terms = ['Test', 'Patient', 'TEST001', '555-0123']
        
        for term in search_terms:
            start_time = time.time()
            response = self.client.get(
                reverse('patient_list'),
                {'search': term}
            )
            end_time = time.time()

            self.assertEqual(response.status_code, 200)
            load_time = end_time - start_time
            self.assertLess(load_time, 0.5)  # Should search in under 0.5 seconds

    def test_concurrent_data_access(self):
        """Test performance with concurrent data access."""
        patient = self.patients[0]
        
        # Simulate concurrent access to different endpoints
        endpoints = [
            reverse('patient_detail', args=[patient.id]),
            reverse('get_latest_vitals', args=[patient.id]),
            reverse('get_latest_labs', args=[patient.id]),
            reverse('medications_api', args=[patient.id])
        ]

        start_time = time.time()
        responses = []
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            responses.append(response)
        end_time = time.time()

        # Verify all responses were successful
        for response in responses:
            self.assertEqual(response.status_code, 200)

        total_time = end_time - start_time
        self.assertLess(total_time, 2.0)  # All concurrent requests should complete in under 2 seconds

    def test_cache_effectiveness(self):
        """Test effectiveness of caching system."""
        patient = self.patients[0]
        endpoint = reverse('patient_detail', args=[patient.id])

        # First request (uncached)
        start_time = time.time()
        response1 = self.client.get(endpoint)
        uncached_time = time.time() - start_time

        # Second request (should be cached)
        start_time = time.time()
        response2 = self.client.get(endpoint)
        cached_time = time.time() - start_time

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertLess(cached_time, uncached_time)  # Cached response should be faster

    def test_form_submission_performance(self):
        """Test performance of form submissions."""
        patient = self.patients[0]
        
        # Test form submission performance
        form_data = {
            'date': date.today().isoformat(),
            'blood_pressure': '120/80',
            'temperature': 98.6,
            'spo2': 98,
            'pulse': 72,
            'respirations': 16,
            'pain': 0,
            'source': 'test'
        }
        
        start_time = time.time()
        response = self.client.post(
            reverse('add_vitals', args=[patient.id]),
            data=form_data
        )
        end_time = time.time()

        self.assertEqual(response.status_code, 302)  # Should redirect after successful submission
        submission_time = end_time - start_time
        self.assertLess(submission_time, 0.5)  # Should submit in under 0.5 seconds

    def test_large_dataset_handling(self):
        """Test handling of large datasets."""
        patient = self.patients[0]
        
        # Create a large number of records for testing
        for i in range(50):
            Vitals.objects.create(
                patient=patient,
                date=date.today() - timedelta(days=i),
                blood_pressure='120/80',
                temperature=98.6,
                spo2=98,
                pulse=72,
                respirations=16,
                pain=0,
                source='test'
            )
            
            Medications.objects.create(
                patient=patient,
                date_prescribed=date.today() - timedelta(days=i),
                drug=f'TestDrug{i}',
                dose='100mg',
                frequency='daily',
                route='oral'
            )
        
        # Test retrieving and rendering large datasets
        start_time = time.time()
        response = self.client.get(reverse('patient_detail', args=[patient.id]))
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        load_time = end_time - start_time
        self.assertLess(load_time, 2.0)  # Should load in under 2 seconds 