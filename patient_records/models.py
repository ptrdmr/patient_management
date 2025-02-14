"""
Patient records models.

This module provides backward compatibility by exposing all models from the new modular structure.
New code should import directly from the models package instead.

DEPRECATED: This file exists only for backward compatibility.
Please import models directly from their respective modules under patient_records.models.*
"""

from .models import (
    # Base models
    BaseModel,
    BasePatientModel,
    BaseReadModel,

    # Patient models
    Patient,
    Provider,

    # Clinical models
    Vitals,
    CmpLabs,
    CbcLabs,
    ClinicalNote,  # Note: Previously ClinicalNotes
    PatientNote,
    NoteTag,
    NoteAttachment,
    Measurements,
    Symptoms,
    Imaging,
    Adls,
    Occurrences,
    Diagnosis,
    Visits,
    Medications,

    # Audit models
    EventStore,
    AuditTrail,
    RecordRequestLog,

    # Read models
    ClinicalReadModel,
    PatientReadModel,
    LabResultsReadModel
)

__all__ = [
    # Base models
    'BaseModel',
    'BasePatientModel',
    'BaseReadModel',

    # Patient models
    'Patient',
    'Provider',

    # Clinical models
    'Vitals',
    'CmpLabs',
    'CbcLabs',
    'ClinicalNote',  # Note: Previously ClinicalNotes
    'PatientNote',
    'NoteTag',
    'NoteAttachment',
    'Measurements',
    'Symptoms',
    'Imaging',
    'Adls',
    'Occurrences',
    'Diagnosis',
    'Visits',
    'Medications',

    # Audit models
    'EventStore',
    'AuditTrail',
    'RecordRequestLog',

    # Read models
    'ClinicalReadModel',
    'PatientReadModel',
    'LabResultsReadModel'
]

# All model definitions have been moved to their respective modules under patient_records.models/
# See the imports above for the new locations

