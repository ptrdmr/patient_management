from typing import Dict, Any, List, Optional
from django.db import transaction
from django.utils import timezone
from ..models import EventStore
from .handlers import PatientEventHandler, ClinicalEventHandler, LabResultEventHandler
import uuid
import logging
from django.core.serializers.json import DjangoJSONEncoder
import json

logger = logging.getLogger(__name__)

class EventStoreService:
    def __init__(self):
        self.handlers = {
            'PATIENT': PatientEventHandler(),
            'CLINICAL': ClinicalEventHandler(),
            'LAB': LabResultEventHandler()
        }

    @staticmethod
    def _get_uuid_from_id(id_value: str) -> uuid.UUID:
        """
        Convert a numeric ID to a UUID by using it as a namespace
        """
        # Use version 5 UUID with DNS namespace and the ID as the name
        return uuid.uuid5(uuid.NAMESPACE_DNS, f"patient-{id_value}")

    def _dispatch_event(self, event: EventStore) -> None:
        """
        Dispatch event to appropriate handler
        """
        handler = self.handlers.get(event.aggregate_type)
        if handler:
            try:
                handler.handle(event.event_type, event.event_data, {
                    'aggregate_id': str(event.aggregate_id),
                    'version': event.version,
                    'timestamp': event.timestamp.isoformat()
                })
            except Exception as e:
                logger.error(f"Error dispatching event: {str(e)}")
                raise

    @transaction.atomic
    def append_event(self, aggregate_id: str, aggregate_type: str, event_type: str, event_data: dict) -> None:
        """
        Append a new event to the event store
        """
        try:
            # Convert UUIDs to strings in event_data
            event_data = json.loads(json.dumps(event_data, cls=DjangoJSONEncoder))
            
            # Validate UUID format
            uuid_obj = uuid.UUID(aggregate_id)
            
            # Get the next version number for this aggregate using select_for_update()
            latest_event = EventStore.objects.filter(
                aggregate_id=str(uuid_obj)
            ).select_for_update().order_by('-version').first()
            
            next_version = 1 if latest_event is None else latest_event.version + 1
            
            # Create and save the event
            event = EventStore.objects.create(
                aggregate_id=str(uuid_obj),
                aggregate_type=aggregate_type,
                event_type=event_type,
                event_data=event_data,
                timestamp=timezone.now(),
                version=next_version
            )
            
            # Dispatch event to handlers
            self._dispatch_event(event)
            
            return event
            
        except ValueError as e:
            logger.error(f"Invalid UUID format for aggregate_id: {aggregate_id}")
            raise
        except Exception as e:
            logger.error(f"Error appending event: {str(e)}")
            raise

    def replay_events(self, aggregate_id: str, up_to_version: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Replay events for a specific aggregate
        """
        query = EventStore.objects.filter(aggregate_id=aggregate_id)
        if up_to_version is not None:
            query = query.filter(version__lte=up_to_version)
        
        events = query.order_by('version')
        return [self._event_to_dict(event) for event in events]

    def get_snapshot(self, aggregate_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the latest snapshot for an aggregate if available
        """
        latest_event = (EventStore.objects
                       .filter(aggregate_id=aggregate_id)
                       .order_by('-version')
                       .first())
        
        if not latest_event:
            return None

        # Replay all events to build current state
        events = self.replay_events(aggregate_id)
        if not events:
            return None

        # Build aggregate state
        aggregate_type = latest_event.aggregate_type
        handler = self.handlers.get(aggregate_type)
        if not handler:
            return None

        current_state = {}
        for event in events:
            event_type = event['event_type']
            event_data = event['event_data']
            metadata = event['metadata']
            handler.handle(event_type, event_data, metadata)
            current_state.update(event_data)

        return current_state

    @staticmethod
    def _event_to_dict(event: EventStore) -> Dict[str, Any]:
        """
        Convert an event to a dictionary representation
        """
        return {
            'id': str(event.id),
            'aggregate_id': str(event.aggregate_id),
            'aggregate_type': event.aggregate_type,
            'event_type': event.event_type,
            'event_data': event.event_data,
            'metadata': event.metadata,
            'version': event.version,
            'timestamp': event.timestamp.isoformat()
        } 