"""Integration tests for clinical notes functionality."""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ...models import Patient, PatientNote, NoteTag, NoteAttachment
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
import json
from datetime import date

class ClinicalNotesTests(TestCase):
    """Test suite for clinical notes functionality."""

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

    def test_create_basic_note(self):
        """Test creation of a basic clinical note."""
        note_data = {
            'patient': self.patient.id,
            'title': 'Test Note',
            'content': 'This is a test note content',
            'category': 'CLINICAL',
            'tags': 'test, clinical',
            'is_pinned': False
        }

        response = self.client.post(
            reverse('create_note'),
            note_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertTrue('noteId' in data)

        # Verify note was created
        note = PatientNote.objects.first()
        self.assertIsNotNone(note)
        self.assertEqual(note.title, 'Test Note')
        self.assertEqual(note.category, 'CLINICAL')
        self.assertEqual(note.created_by, self.user)

        # Verify tags were created
        self.assertEqual(note.tags.count(), 2)
        tag_names = [tag.name for tag in note.tags.all()]
        self.assertIn('test', tag_names)
        self.assertIn('clinical', tag_names)

    def test_create_note_with_attachment(self):
        """Test creation of a note with file attachment."""
        # Create a test file
        test_file = SimpleUploadedFile(
            "test_file.txt",
            b"This is a test file content",
            content_type="text/plain"
        )

        note_data = {
            'patient': self.patient.id,
            'title': 'Note with Attachment',
            'content': 'This note has an attachment',
            'category': 'GENERAL',
            'attachments': [test_file]
        }

        response = self.client.post(
            reverse('create_note'),
            note_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])

        # Verify note and attachment were created
        note = PatientNote.objects.first()
        self.assertIsNotNone(note)
        self.assertEqual(note.attachments.count(), 1)
        attachment = note.attachments.first()
        self.assertEqual(attachment.filename, 'test_file.txt')

    def test_edit_note(self):
        """Test editing an existing note."""
        # Create initial note
        note = PatientNote.objects.create(
            patient=self.patient,
            title='Original Title',
            content='Original content',
            category='GENERAL',
            created_by=self.user
        )

        # Add initial tag
        tag = NoteTag.objects.create(name='initial')
        note.tags.add(tag)

        # Edit data
        edit_data = {
            'patient': self.patient.id,
            'title': 'Updated Title',
            'content': 'Updated content',
            'category': 'CLINICAL',
            'tags': 'updated, new',
            'is_pinned': True
        }

        response = self.client.post(
            reverse('edit_note', args=[note.id]),
            edit_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])

        # Verify changes
        note.refresh_from_db()
        self.assertEqual(note.title, 'Updated Title')
        self.assertEqual(note.content, 'Updated content')
        self.assertEqual(note.category, 'CLINICAL')
        self.assertTrue(note.is_pinned)

        # Verify tags were updated
        self.assertEqual(note.tags.count(), 2)
        new_tag_names = [tag.name for tag in note.tags.all()]
        self.assertIn('updated', new_tag_names)
        self.assertIn('new', new_tag_names)
        self.assertNotIn('initial', new_tag_names)

    def test_delete_note(self):
        """Test note deletion."""
        note = PatientNote.objects.create(
            patient=self.patient,
            title='Test Note',
            content='Content to delete',
            category='GENERAL',
            created_by=self.user
        )

        response = self.client.post(
            reverse('delete_note', args=[note.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertFalse(PatientNote.objects.exists())

    def test_toggle_pin_note(self):
        """Test toggling note pin status."""
        note = PatientNote.objects.create(
            patient=self.patient,
            title='Test Note',
            content='Test content',
            category='GENERAL',
            created_by=self.user,
            is_pinned=False
        )

        # Pin the note
        response = self.client.post(
            reverse('toggle_pin_note', args=[note.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])

        note.refresh_from_db()
        self.assertTrue(note.is_pinned)

        # Unpin the note
        response = self.client.post(
            reverse('toggle_pin_note', args=[note.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        note.refresh_from_db()
        self.assertFalse(note.is_pinned)

    def test_invalid_note_creation(self):
        """Test creation with invalid data."""
        invalid_data = {
            'patient': self.patient.id,
            'title': '',  # Required field
            'content': '',  # Required field
            'category': 'INVALID'  # Invalid choice
        }

        response = self.client.post(
            reverse('create_note'),
            invalid_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertTrue('errors' in data)
        self.assertFalse(PatientNote.objects.exists())

    def test_unauthorized_note_access(self):
        """Test note access by unauthorized user."""
        self.client.logout()
        
        note_data = {
            'patient': self.patient.id,
            'title': 'Test Note',
            'content': 'This is a test note',
            'category': 'GENERAL'
        }

        response = self.client.post(
            reverse('create_note'),
            note_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertFalse(PatientNote.objects.exists())

    def test_note_filtering(self):
        """Test note filtering functionality."""
        # Create notes with different categories
        clinical_note = PatientNote.objects.create(
            patient=self.patient,
            title='Clinical Note',
            content='Clinical content',
            category='CLINICAL',
            created_by=self.user
        )
        general_note = PatientNote.objects.create(
            patient=self.patient,
            title='General Note',
            content='General content',
            category='GENERAL',
            created_by=self.user
        )

        # Test filtering by category
        response = self.client.get(
            reverse('patient_notes'),
            {'patient': self.patient.id, 'category': 'CLINICAL'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 1) 