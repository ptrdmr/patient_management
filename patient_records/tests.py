from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Provider, Patient
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
