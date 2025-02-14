"""Test event store functionality."""

from django.test import TestCase
from django.core.exceptions import ValidationError
from ..models import EventStore
import uuid

class EventStoreTests(TestCase):
    """Test cases for EventStore model."""

    def setUp(self):
        """Set up test data."""
        self.aggregate_id = str(uuid.uuid4())
        self.base_event = {
            'aggregate_type': 'PATIENT',
            'aggregate_id': self.aggregate_id,
            'event_type': 'PATIENT_REGISTERED',
            'event_data': {'test': 'data'},
            'metadata': {},
            'sequence': 1
        }

    def test_sequence_must_be_positive(self):
        """Test that sequence numbers must be positive."""
        event_data = self.base_event.copy()
        event_data['sequence'] = 0
        event = EventStore(**event_data)
        with self.assertRaises(ValidationError) as context:
            event.full_clean()
        self.assertIn('sequence', str(context.exception))

    def test_sequence_must_be_consecutive(self):
        """Test that sequence numbers must be consecutive."""
        # Create first event
        first_event = self.base_event.copy()
        first_event['sequence'] = 1
        EventStore.objects.create(**first_event)

        # Try to create event with non-consecutive sequence
        second_event = self.base_event.copy()
        second_event['sequence'] = 3
        event = EventStore(**second_event)
        with self.assertRaises(ValidationError) as context:
            event.full_clean()
        self.assertIn('sequence', str(context.exception))

    def test_valid_consecutive_sequence(self):
        """Test that consecutive sequence numbers are valid."""
        # Create first event
        first_event = self.base_event.copy()
        first_event['sequence'] = 1
        EventStore.objects.create(**first_event)

        # Create second event with consecutive sequence
        second_event = self.base_event.copy()
        second_event['sequence'] = 2
        event = EventStore(**second_event)
        try:
            event.full_clean()
            event.save()
        except ValidationError as e:
            self.fail(f"Consecutive sequence should be valid: {str(e)}")

    def test_unique_sequence_per_aggregate(self):
        """Test that sequence numbers are unique per aggregate."""
        # Create event for first aggregate
        first_event = self.base_event.copy()
        first_event['sequence'] = 1
        EventStore.objects.create(**first_event)

        # Create event for different aggregate with same sequence
        different_aggregate = self.base_event.copy()
        different_aggregate['aggregate_id'] = str(uuid.uuid4())
        different_aggregate['sequence'] = 1
        event = EventStore(**different_aggregate)
        try:
            event.full_clean()
            event.save()
        except ValidationError as e:
            self.fail(f"Same sequence for different aggregate should be valid: {str(e)}")

    def test_metadata_can_be_empty(self):
        """Test that metadata can be an empty dict."""
        event = EventStore(**self.base_event)
        try:
            event.full_clean()
            event.save()
        except ValidationError as e:
            self.fail(f"Empty metadata should be valid: {str(e)}")
        self.assertEqual(event.metadata, {}) 