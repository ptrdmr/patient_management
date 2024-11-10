from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Provider, Patient
from .forms import (
    ProviderForm, PatientForm, DiagnosisForm, VitalsForm,
    MedicationsForm, MeasurementsForm, SymptomsForm,
    CmpLabsForm, CbcLabsForm
)
import datetime

class ViewsTestCase(TestCase):
    def setUp(self):
        # Create test user
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Create test provider with required fields
        self.provider = Provider.objects.create(
            date=datetime.date.today(),
            provider='Test Provider',
            practice='Test Practice',
            address='123 Test St',
            city='Test City',
            state='Test State',
            zip='12345'
        )

        # Create test patient for form tests
        self.test_patient = Patient.objects.create(
            first_name="Test",
            last_name="Patient",
            date_of_birth="1990-01-01",
            date=datetime.date.today(),  # Add this line
            ssn="123-45-6789"
        )

    def test_provider_list(self):
        """Test provider list view"""
        response = self.client.get(reverse('provider_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Provider')
        self.assertContains(response, 'Test Practice')

    def test_add_provider(self):
        """Test adding a provider"""
        data = {
            'date': '2024-01-01',
            'provider': 'New Provider',
            'practice': 'New Practice',
            'address': '456 New St',
            'city': 'New City',
            'state': 'New State',
            'zip': '67890',
            'fax': '123-456-7890',  # Optional
            'phone': '098-765-4321',  # Optional
            'source': 'Test Source'   # Optional
        }
        response = self.client.post(reverse('add_provider'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Provider.objects.filter(provider='New Provider').exists())

    def test_edit_provider(self):
        """Test editing a provider"""
        data = {
            'date': '2024-01-01',
            'provider': 'Updated Provider',
            'practice': 'Updated Practice',
            'address': '789 Update St',
            'city': 'Update City',
            'state': 'Update State',
            'zip': '11111'
        }
        response = self.client.post(
            reverse('edit_provider', args=[self.provider.id]), 
            data
        )
        self.assertEqual(response.status_code, 302)
        updated_provider = Provider.objects.get(id=self.provider.id)
        self.assertEqual(updated_provider.provider, 'Updated Provider')

class FormSectionTests(TestCase):
    def test_provider_form_sections(self):
        """Test provider form sections"""
        form = ProviderForm()
        self.assertTrue(hasattr(form, 'sections'))
        
        # Verify all sections have required keys
        for section in form.sections:
            self.assertIn('title', section)
            self.assertIn('description', section)
            self.assertIn('fields', section)
        
        # Verify all form fields are included in sections
        all_section_fields = [field for section in form.sections for field in section['fields']]
        for field in form.fields:
            self.assertIn(field, all_section_fields)

    def test_lab_form_sections(self):
        """Test CMP and CBC lab form sections"""
        # Test CMP form sections
        cmp_form = CmpLabsForm()
        self.assertTrue(hasattr(cmp_form, 'sections'))
        cmp_section_titles = [section['title'] for section in cmp_form.sections]
        expected_cmp_titles = [
            'Basic Information',
            'Metabolic Panel',
            'Liver Function',
            'Electrolytes',
            'Additional Tests'
        ]
        self.assertEqual(cmp_section_titles, expected_cmp_titles)

        # Test CBC form sections
        cbc_form = CbcLabsForm()
        self.assertTrue(hasattr(cbc_form, 'sections'))
        cbc_section_titles = [section['title'] for section in cbc_form.sections]
        expected_cbc_titles = [
            'Basic Information',
            'Red Blood Cell Counts',
            'White Blood Cell Counts',
            'Cell Indices',
            'Platelets'
        ]
        self.assertEqual(cbc_section_titles, expected_cbc_titles)

    def test_form_field_coverage(self):
        """Test that all form fields are included in sections"""
        forms_to_test = [
            ProviderForm(),
            CmpLabsForm(),
            CbcLabsForm()
        ]

        for form in forms_to_test:
            all_section_fields = [field for section in form.sections for field in section['fields']]
            for field in form.fields:
                self.assertIn(field, all_section_fields, 
                    f"Field '{field}' missing from sections in {form.__class__.__name__}")

    def test_medical_field_validation(self):
        """Test that medical fields have proper validation rules"""
        form = MeasurementsForm()
        
        # Test blood pressure validation
        self.assertEqual(
            form.fields['blood_pressure'].widget.attrs['pattern'],
            r'^\d{2,3}\/\d{2,3}$'
        )
        
        # Test temperature validation
        self.assertEqual(form.fields['temperature'].widget.attrs['min'], '95')
        self.assertEqual(form.fields['temperature'].widget.attrs['max'], '108')
        
        # Test pulse validation
        self.assertEqual(form.fields['pulse'].widget.attrs['min'], '40')
        self.assertEqual(form.fields['pulse'].widget.attrs['max'], '200')
