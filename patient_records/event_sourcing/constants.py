"""Constants for event sourcing system"""

# Clinical Events
VITALS_RECORDED = 'VitalsRecorded'
DIAGNOSIS_ADDED = 'DiagnosisAdded'
SYMPTOMS_ADDED = 'SymptomsAdded'
SYMPTOMS_UPDATED = 'SymptomsUpdated'
MEDICATION_PRESCRIBED = 'MedicationPrescribed'
MEDICATION_DISCONTINUED = 'MedicationDiscontinued'

# Patient Events
PATIENT_REGISTERED = 'PatientRegistered'
PATIENT_UPDATED = 'PatientUpdated'
PATIENT_ARCHIVED = 'PatientArchived'

# Lab Events
LAB_RESULT_RECORDED = 'LabResultRecorded'
LAB_RESULT_UPDATED = 'LabResultUpdated'
LAB_RESULT_CANCELLED = 'LabResultCancelled'

# Security Events
AUTH_FAILURE = 'AUTH_FAILURE'
BRUTE_FORCE = 'BRUTE_FORCE'

# Aggregate Types
PATIENT_AGGREGATE = 'PATIENT'
CLINICAL_AGGREGATE = 'CLINICAL'
LAB_AGGREGATE = 'LAB'
SECURITY_AGGREGATE = 'SECURITY' 