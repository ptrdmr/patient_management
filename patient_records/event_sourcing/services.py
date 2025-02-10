from typing import Dict, Any, List, Optional
from django.db import transaction
from django.utils import timezone
from .models import EventStore
from .handlers import PatientEventHandler, ClinicalEventHandler, LabResultEventHandler
import uuid
from django.db.models import QuerySet
import logging

logger = logging.getLogger(__name__)

class EventStoreService:
    def __init__(self):
        self.handlers = {
            'PATIENT': PatientEventHandler(),
            'CLINICAL': ClinicalEventHandler(),
            'LAB': LabResultEventHandler()
        }

    def append_event(self, aggregate_id: str, aggregate_type: str, event_type: str, event_data: dict) -> None:
        """
        Append a new event to the event store
        """
        try:
            # Validate UUID format
            uuid_obj = uuid.UUID(aggregate_id)
            
            # Get the latest version for this aggregate
            latest_event = EventStore.objects.filter(
                aggregate_id=str(uuid_obj)
            ).order_by('-version').first()
            
            # Calculate the next version
            next_version = (latest_event.version + 1) if latest_event else 1
            
            # Create timestamp for both event and metadata
            timestamp = timezone.now()
            timestamp_str = timestamp.isoformat()
            
            # Create and save the event
            event = EventStore.objects.create(
                aggregate_id=str(uuid_obj),
                aggregate_type=aggregate_type,
                event_type=event_type,
                event_data=event_data,
                version=next_version,
                timestamp=timestamp,
                metadata={'timestamp': timestamp_str}
            )
            
            # Dispatch event to handlers
            handler = self.handlers.get(aggregate_type)
            if handler:
                handler.handle(event_type, event_data, {'timestamp': timestamp_str})
                
        except ValueError as e:
            logger.error(f"Invalid UUID format for aggregate_id: {aggregate_id}")
            raise
        except Exception as e:
            logger.error(f"Error appending event: {str(e)}")
            raise

    def get_events(self, aggregate_id: str, event_type: Optional[str] = None) -> QuerySet:
        """
        Get all events for a specific aggregate
        """
        try:
            uuid_obj = uuid.UUID(aggregate_id)
            events = EventStore.objects.filter(aggregate_id=uuid_obj)
            if event_type:
                events = events.filter(event_type=event_type)
            return events.order_by('timestamp')
        except ValueError as e:
            logger.error(f"Invalid UUID format for aggregate_id: {aggregate_id}")
            raise 