from typing import Dict, Any, List, Optional
from django.db import transaction
from django.utils import timezone
from ..models.event_sourcing import EventStore
from .handlers import PatientEventHandler, ClinicalEventHandler, LabResultEventHandler

class EventStoreService:
    def __init__(self):
        self.handlers = {
            'PATIENT': PatientEventHandler(),
            'CLINICAL': ClinicalEventHandler(),
            'LAB': LabResultEventHandler()
        }

    @transaction.atomic
    def append_event(self, aggregate_id: str, aggregate_type: str, 
                    event_type: str, event_data: Dict[str, Any],
                    metadata: Optional[Dict[str, Any]] = None) -> EventStore:
        """
        Append a new event to the event store and update the read model
        """
        # Get the current version for this aggregate
        current_version = EventStore.objects.filter(aggregate_id=aggregate_id).count()
        
        # Create the event
        event = EventStore.objects.create(
            aggregate_id=aggregate_id,
            aggregate_type=aggregate_type,
            event_type=event_type,
            event_data=event_data,
            metadata=metadata or {},
            version=current_version + 1,
            timestamp=timezone.now()
        )

        # Update the read model
        handler = self.handlers.get(aggregate_type)
        if handler:
            handler.handle(event_type, event_data, metadata)

        return event

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