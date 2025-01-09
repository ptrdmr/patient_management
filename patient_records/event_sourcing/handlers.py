from abc import ABC, abstractmethod
from typing import Dict, Any, List
from django.db import transaction
from ..models.event_sourcing import EventStore, PatientReadModel, ClinicalReadModel, LabResultsReadModel

class EventHandler(ABC):
    def __init__(self):
        self.handlers = {}
        self.register_handlers()

    @abstractmethod
    def register_handlers(self):
        pass

    def handle(self, event_type: str, event_data: Dict[str, Any], metadata: Dict[str, Any] = None):
        if event_type not in self.handlers:
            raise ValueError(f"No handler registered for event type: {event_type}")
        
        handler = self.handlers[event_type]
        return handler(event_data, metadata)

class PatientEventHandler(EventHandler):
    def register_handlers(self):
        self.handlers = {
            'PatientRegistered': self._handle_patient_registered,
            'PatientUpdated': self._handle_patient_updated,
            'PatientArchived': self._handle_patient_archived
        }

    @transaction.atomic
    def _handle_patient_registered(self, event_data: Dict[str, Any], metadata: Dict[str, Any] = None):
        # Create new patient read model
        patient = PatientReadModel.objects.create(
            id=event_data['id'],
            current_data=event_data,
            version=1,
            last_updated=metadata.get('timestamp') if metadata else None
        )
        return patient

    @transaction.atomic
    def _handle_patient_updated(self, event_data: Dict[str, Any], metadata: Dict[str, Any] = None):
        patient = PatientReadModel.objects.select_for_update().get(id=event_data['id'])
        patient.current_data.update(event_data['updates'])
        patient.version += 1
        patient.last_updated = metadata.get('timestamp') if metadata else None
        patient.save()
        return patient

    @transaction.atomic
    def _handle_patient_archived(self, event_data: Dict[str, Any], metadata: Dict[str, Any] = None):
        patient = PatientReadModel.objects.select_for_update().get(id=event_data['id'])
        patient.current_data['status'] = 'archived'
        patient.version += 1
        patient.last_updated = metadata.get('timestamp') if metadata else None
        patient.save()
        return patient

class ClinicalEventHandler(EventHandler):
    def register_handlers(self):
        self.handlers = {
            'VitalSignsRecorded': self._handle_vitals_recorded,
            'DiagnosisAdded': self._handle_diagnosis_added,
            'MedicationPrescribed': self._handle_medication_prescribed,
            'MedicationDiscontinued': self._handle_medication_discontinued
        }

    @transaction.atomic
    def _handle_vitals_recorded(self, event_data: Dict[str, Any], metadata: Dict[str, Any] = None):
        return ClinicalReadModel.objects.create(
            patient_id=event_data['patient_id'],
            event_type='VitalSignsRecorded',
            data=event_data,
            recorded_at=metadata.get('timestamp') if metadata else None
        )

    # Similar handlers for other clinical events...

class LabResultEventHandler(EventHandler):
    def register_handlers(self):
        self.handlers = {
            'LabResultRecorded': self._handle_lab_result_recorded,
            'LabResultUpdated': self._handle_lab_result_updated,
            'LabResultCancelled': self._handle_lab_result_cancelled
        }

    @transaction.atomic
    def _handle_lab_result_recorded(self, event_data: Dict[str, Any], metadata: Dict[str, Any] = None):
        return LabResultsReadModel.objects.create(
            patient_id=event_data['patient_id'],
            lab_type=event_data['lab_type'],
            results=event_data['results'],
            performed_at=metadata.get('timestamp') if metadata else None
        ) 