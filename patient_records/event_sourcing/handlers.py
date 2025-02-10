from abc import ABC, abstractmethod
from typing import Dict, Any, List
from django.db import transaction
from .models import EventStore
from .constants import *
import logging

logger = logging.getLogger(__name__)

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
            PATIENT_REGISTERED: self._handle_patient_registered,
            PATIENT_UPDATED: self._handle_patient_updated,
            PATIENT_ARCHIVED: self._handle_patient_archived
        }

    @transaction.atomic
    def _handle_patient_registered(self, event_data: Dict[str, Any], metadata: Dict[str, Any] = None):
        from ..models import PatientReadModel  # Import here to avoid circular import
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
        from ..models import PatientReadModel  # Import here to avoid circular import
        patient = PatientReadModel.objects.select_for_update().get(id=event_data['id'])
        patient.current_data.update(event_data['updates'])
        patient.version += 1
        patient.last_updated = metadata.get('timestamp') if metadata else None
        patient.save()
        return patient

    @transaction.atomic
    def _handle_patient_archived(self, event_data: Dict[str, Any], metadata: Dict[str, Any] = None):
        from ..models import PatientReadModel  # Import here to avoid circular import
        patient = PatientReadModel.objects.select_for_update().get(id=event_data['id'])
        patient.current_data['status'] = 'archived'
        patient.version += 1
        patient.last_updated = metadata.get('timestamp') if metadata else None
        patient.save()
        return patient

class ClinicalEventHandler(EventHandler):
    def register_handlers(self):
        self.handlers = {
            VITALS_RECORDED: self._handle_vitals_recorded,
            DIAGNOSIS_ADDED: self._handle_diagnosis_added,
            SYMPTOMS_ADDED: self._handle_symptoms_added,
            SYMPTOMS_UPDATED: self._handle_symptoms_added,
            MEDICATION_PRESCRIBED: self._handle_medication_prescribed,
            MEDICATION_DISCONTINUED: self._handle_medication_discontinued
        }

    @transaction.atomic
    def _handle_vitals_recorded(self, event_data: Dict[str, Any], metadata: Dict[str, Any] = None):
        from ..models import ClinicalReadModel  # Import here to avoid circular import
        try:
            return ClinicalReadModel.objects.create(
                patient_id=event_data['patient_id'],
                event_type=VITALS_RECORDED,
                data=event_data,
                recorded_at=metadata.get('timestamp') if metadata else None
            )
        except Exception as e:
            logger.error(f"Error handling vitals recording: {str(e)}")
            raise

    @transaction.atomic
    def _handle_diagnosis_added(self, event_data: Dict[str, Any], metadata: Dict[str, Any] = None):
        from ..models import ClinicalReadModel  # Import here to avoid circular import
        try:
            model = ClinicalReadModel.objects.create(
                patient_id=event_data['patient_id'],
                event_type=DIAGNOSIS_ADDED,
                data=event_data,
                recorded_at=metadata.get('timestamp') if metadata else None
            )
            if 'provider' in event_data:
                model.update_provider_details(event_data['provider'])
                model.save()
            return model
        except Exception as e:
            logger.error(f"Error handling diagnosis addition: {str(e)}")
            raise

    @transaction.atomic
    def _handle_symptoms_added(self, event_data: Dict[str, Any], metadata: Dict[str, Any] = None):
        from ..models import ClinicalReadModel  # Import here to avoid circular import
        try:
            model = ClinicalReadModel.objects.create(
                patient_id=event_data['patient_id'],
                event_type=event_data.get('event_type', SYMPTOMS_ADDED),
                data=event_data,
                recorded_at=metadata.get('timestamp') if metadata else None
            )
            
            # Update the denormalized symptoms summary
            symptoms_data = {
                'symptom': event_data.get('symptom'),
                'severity': event_data.get('severity'),
                'notes': event_data.get('notes'),
                'recorded_at': metadata.get('timestamp'),
                'person_reporting': event_data.get('person_reporting')
            }
            model.update_symptoms_summary(symptoms_data)
            
            # Update provider details if present
            if 'provider_id' in event_data:
                model.update_provider_details({'provider_id': event_data['provider_id']})
            
            model.save()
            return model
        except Exception as e:
            logger.error(f"Error handling symptoms addition/update: {str(e)}")
            raise

    @transaction.atomic
    def _handle_medication_prescribed(self, event_data: Dict[str, Any], metadata: Dict[str, Any] = None):
        try:
            model = ClinicalReadModel.objects.create(
                patient_id=event_data['patient_id'],
                event_type=MEDICATION_PRESCRIBED,
                data=event_data,
                recorded_at=metadata.get('timestamp') if metadata else None
            )
            if 'provider' in event_data:
                model.update_provider_details(event_data['provider'])
                model.save()
            return model
        except Exception as e:
            logger.error(f"Error handling medication prescription: {str(e)}")
            raise

    @transaction.atomic
    def _handle_medication_discontinued(self, event_data: Dict[str, Any], metadata: Dict[str, Any] = None):
        try:
            model = ClinicalReadModel.objects.create(
                patient_id=event_data['patient_id'],
                event_type=MEDICATION_DISCONTINUED,
                data=event_data,
                recorded_at=metadata.get('timestamp') if metadata else None
            )
            if 'provider' in event_data:
                model.update_provider_details(event_data['provider'])
                model.save()
            return model
        except Exception as e:
            logger.error(f"Error handling medication discontinuation: {str(e)}")
            raise

class LabResultEventHandler(EventHandler):
    def register_handlers(self):
        self.handlers = {
            LAB_RESULT_RECORDED: self._handle_lab_result_recorded,
            LAB_RESULT_UPDATED: self._handle_lab_result_updated,
            LAB_RESULT_CANCELLED: self._handle_lab_result_cancelled
        }

    @transaction.atomic
    def _handle_lab_result_recorded(self, event_data: Dict[str, Any], metadata: Dict[str, Any] = None):
        from ..models import LabResultsReadModel  # Import here to avoid circular import
        try:
            return LabResultsReadModel.objects.create(
                patient_id=event_data['patient_id'],
                lab_type=event_data['lab_type'],
                results=event_data['results'],
                performed_at=metadata.get('timestamp') if metadata else None
            )
        except Exception as e:
            logger.error(f"Error handling lab result recording: {str(e)}")
            raise

    @transaction.atomic
    def _handle_lab_result_updated(self, event_data: Dict[str, Any], metadata: Dict[str, Any] = None):
        from ..models import LabResultsReadModel  # Import here to avoid circular import
        try:
            result = LabResultsReadModel.objects.select_for_update().get(id=event_data['id'])
            result.results.update(event_data['updates'])
            result.save()
            return result
        except Exception as e:
            logger.error(f"Error handling lab result update: {str(e)}")
            raise

    @transaction.atomic
    def _handle_lab_result_cancelled(self, event_data: Dict[str, Any], metadata: Dict[str, Any] = None):
        from ..models import LabResultsReadModel  # Import here to avoid circular import
        try:
            result = LabResultsReadModel.objects.select_for_update().get(id=event_data['id'])
            result.results['status'] = 'cancelled'
            result.save()
            return result
        except Exception as e:
            logger.error(f"Error handling lab result cancellation: {str(e)}")
            raise 