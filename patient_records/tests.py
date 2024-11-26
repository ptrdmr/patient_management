from django.test import TestCase, Client
from django.urls import reverse, NoReverseMatch
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Provider, Patient, Visits, Adls, AuditTrail
from .forms import (
    ProviderForm, PatientForm, DiagnosisForm, VitalsForm,
    MedicationsForm, MeasurementsForm, SymptomsForm,
    CmpLabsForm, CbcLabsForm,
    VisitsForm,
    AdlsForm,
    ImagingForm,
    RecordRequestLogForm
)
import datetime
from django.db import connection
from django.test.utils import CaptureQueriesContext
import logging
import warnings
from django.test import override_settings

# Suppress logging and warnings
logging.disable(logging.CRITICAL)
warnings.filterwarnings('ignore', message='No directory at*')

def create_test_patient():
    """Helper function to create a test patient with all required fields"""
    return Patient.objects.create(
        date=timezone.now().date(),
        first_name="Test",
        last_name="Patient",
        date_of_birth=timezone.now().date() - datetime.timedelta(days=10000),
        poa_name="Test POA",
        poa_contact="123-456-7890",
        ssn="123-45-6789",
        gender='M',
        street_address='123 Test St',
        city='Test City',
        state='Test State',
        zip='12345'
    )

def create_test_provider():
    """Helper function to create a test provider with all required fields"""
    return Provider.objects.create(
        date=timezone.now().date(),
        provider='Test Provider',
        practice='Test Practice',
        address='123 Test St',
        city='Test City',
        state='Test State',
        zip='12345',
        phone='555-1234',
        fax='555-5678',
        source='Manual Entry'
    )

class BaseTestCase(TestCase):
    """Base test case with common setup"""
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client.force_login(self.user)
        self.patient = create_test_patient()
        self.provider = create_test_provider()

@override_settings(STATICFILES_DIRS=[])
class ViewsTestCase(BaseTestCase):
    def test_provider_list(self):
        """Test provider list view"""
        response = self.client.get(reverse('provider_list'))
        self.assertEqual(response.status_code, 200)
        
        # Test for specific provider data
        self.assertContains(response, self.provider.provider)
        self.assertContains(response, self.provider.practice)
        self.assertContains(response, f"{self.provider.city}, {self.provider.state}")
        
        # Test for table structure
        self.assertContains(response, '<table class="data-table">')
        self.assertContains(response, '<th>Provider Name</th>')

    def test_patient_list(self):
        """Test patient list view"""
        response = self.client.get(reverse('patient_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.patient.first_name)
        self.assertContains(response, self.patient.last_name)

class FormSectionTests(BaseTestCase):
    def test_provider_form_sections(self):
        """Test that ProviderForm has correct sections"""
        self.maxDiff = None
        form = ProviderForm()
        expected_sections = [
            {
                'title': 'Provider Information',
                'fields': ['provider', 'practice']
            },
            {
                'title': 'Contact Information',
                'fields': ['address', 'city', 'state', 'zip', 'phone', 'fax']
            },
            {
                'title': 'Additional Information',
                'fields': ['source']
            }
        ]
        self.assertEqual(form.get_sections(), expected_sections)

    def test_cmp_labs_form_sections(self):
        """Test that CmpLabsForm has correct sections"""
        self.maxDiff = None
        form = CmpLabsForm()
        expected_sections = [
            {
                'title': 'Basic Information',
                'description': 'Date of lab results',
                'fields': ['date']
            },
            {
                'title': 'Electrolytes',
                'description': 'Electrolyte measurements',
                'fields': ['sodium', 'potassium', 'chloride', 'co2']
            },
            {
                'title': 'Metabolic Panel',
                'description': 'Basic metabolic measurements',
                'fields': ['glucose', 'bun', 'creatinine', 'calcium']
            },
            {
                'title': 'Liver Function',
                'description': 'Liver function tests',
                'fields': ['protein', 'albumin', 'bilirubin', 'gfr']
            }
        ]
        self.assertEqual(form.get_sections(), expected_sections)

class FormValidationTests(BaseTestCase):
    def test_visit_form_valid(self):
        """Test that VisitsForm is valid with correct data"""
        form_data = {
            'date': timezone.now().date(),
            'visit_type': 'Office Visit',
            'provider': self.provider.id,
            'practice': self.provider.practice,
            'notes': 'Routine check-up',
            'source': 'Manual Entry'
        }
        form = VisitsForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_visit_form_invalid_future_date(self):
        """Test that VisitsForm is invalid with a future date"""
        future_date = timezone.now().date() + datetime.timedelta(days=1)
        form_data = {
            'date': future_date,
            'visit_type': 'Office Visit',
            'provider': self.provider.id,
            'practice': 'Test Practice',
            'source': 'Manual Entry'
        }
        form = VisitsForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('date', form.errors)
        self.assertEqual(form.errors['date'][0], 'Future dates are not allowed.')

class ModelTests(BaseTestCase):
    def test_patient_str(self):
        """Test the string representation of Patient"""
        self.assertEqual(
            str(self.patient),
            f"{self.patient.first_name} {self.patient.last_name}"
        )

    def test_provider_str(self):
        """Test the string representation of Provider"""
        self.assertEqual(str(self.provider), self.provider.provider)

class URLPatternTests(BaseTestCase):
    def test_url_patterns(self):
        """Test that all required URL patterns exist"""
        urls_to_test = [
            ('home', []),
            ('provider_list', []),
            ('add_provider', []),
            ('edit_provider', [self.provider.id]),
            ('patient_list', []),
            ('add_patient', []),
            ('patient_detail', [self.patient.id]),
            ('add_visit', [self.patient.id]),
            ('add_vitals', [self.patient.id]),
            ('add_labs', [self.patient.id]),
            ('add_medications', [self.patient.id]),
            ('patient_tab_data', [self.patient.id, 'visits']),
        ]

        for url_name, args in urls_to_test:
            try:
                reverse(url_name, args=args)
            except NoReverseMatch as e:
                self.fail(f"URL pattern '{url_name}' not found: {e}")

class TemplateTests(BaseTestCase):
    def test_form_renders_correctly(self):
        """Test form HTML structure"""
        response = self.client.get(reverse('add_visit', args=[self.patient.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'patient_records/add_visit.html')

        # Test form structure
        self.assertContains(response, '<form')
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, 'btn primary')
        self.assertContains(response, 'btn secondary')
        
        # Test form fields are present
        self.assertContains(response, 'name="date"')
        self.assertContains(response, 'name="visit_type"')
        self.assertContains(response, 'name="provider"')

    def test_error_message_display(self):
        """Test error message rendering"""
        response = self.client.post(reverse('add_visit', args=[self.patient.id]), {})
        self.assertContains(response, 'This field is required')

class PerformanceTests(BaseTestCase):
    def test_query_count(self):
        """Test number of queries executed"""
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(reverse('patient_detail', args=[self.patient.id]))
            self.assertEqual(response.status_code, 200, "Page should load successfully")
            
            # Count queries by type
            select_count = sum(1 for q in context.captured_queries 
                             if q['sql'].startswith('SELECT'))
            
            # Assert reasonable query counts
            self.assertLess(select_count, 10, "Too many SELECT queries")

class SearchTests(BaseTestCase):
    def test_patient_search(self):
        """Test patient search functionality"""
        response = self.client.get(reverse('patient_list'), {'q': self.patient.last_name})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.patient.last_name)

        # Test partial matches
        response = self.client.get(
            reverse('patient_list'),
            {'q': self.patient.last_name[:2]}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.patient.last_name)
