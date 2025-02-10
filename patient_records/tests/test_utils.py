"""Test utilities for patient records app"""
from typing import Dict, Any, List
from ..event_sourcing.constants import *
from ..models import EventStore

def validate_event_store_entry(
    event_store_entry: EventStore,
    expected_aggregate_type: str,
    expected_event_type: str,
    expected_data_keys: List[str]
) -> List[str]:
    """
    Validate an event store entry against expected values
    Returns a list of validation errors, empty list means validation passed
    """
    errors = []
    
    # Check aggregate type
    if event_store_entry.aggregate_type != expected_aggregate_type:
        errors.append(
            f"Incorrect aggregate_type: expected '{expected_aggregate_type}', "
            f"got '{event_store_entry.aggregate_type}'"
        )
    
    # Check event type
    if event_store_entry.event_type != expected_event_type:
        errors.append(
            f"Incorrect event_type: expected '{expected_event_type}', "
            f"got '{event_store_entry.event_type}'"
        )
    
    # Check data keys
    for key in expected_data_keys:
        if key not in event_store_entry.event_data:
            errors.append(f"Missing required key in event_data: '{key}'")
    
    return errors

def get_expected_event_data() -> Dict[str, Dict[str, Any]]:
    """
    Get expected event data structure for each event type
    """
    return {
        VITALS_RECORDED: {
            'aggregate_type': CLINICAL_AGGREGATE,
            'required_keys': [
                'patient_id', 'vitals_id', 'date', 'blood_pressure',
                'temperature', 'spo2', 'pulse', 'respirations',
                'supp_o2', 'pain', 'source'
            ]
        },
        DIAGNOSIS_ADDED: {
            'aggregate_type': CLINICAL_AGGREGATE,
            'required_keys': [
                'patient_id', 'diagnosis_id', 'date', 'icd_code',
                'diagnosis', 'notes', 'source'
            ]
        },
        SYMPTOMS_ADDED: {
            'aggregate_type': CLINICAL_AGGREGATE,
            'required_keys': [
                'patient_id', 'symptoms_id', 'date', 'symptom',
                'notes', 'source', 'person_reporting'
            ]
        },
        MEDICATION_PRESCRIBED: {
            'aggregate_type': CLINICAL_AGGREGATE,
            'required_keys': [
                'patient_id', 'medication_id', 'date', 'drug',
                'dose', 'route', 'frequency', 'source'
            ]
        },
        MEDICATION_DISCONTINUED: {
            'aggregate_type': CLINICAL_AGGREGATE,
            'required_keys': [
                'patient_id', 'medication_id', 'date', 'reason',
                'source'
            ]
        },
        LAB_RESULT_RECORDED: {
            'aggregate_type': LAB_AGGREGATE,
            'required_keys': [
                'patient_id', 'lab_id', 'lab_type', 'date',
                'results', 'source'
            ]
        }
    } 