from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.forms import model_to_dict
import logging
import decimal
import datetime

from .models import (
    Patient, CbcLabs, CmpLabs, Medications, 
    Symptoms, Diagnosis, Visits, ClinicalNote,
    Measurements, Imaging, Adls, Occurrences,
    AuditTrail
)

# Initialize logger
logger = logging.getLogger('patient_records')

@receiver(post_save, sender=Patient)
def log_patient_save(sender, instance, created, **kwargs):
    action = 'CREATE' if created else 'UPDATE'
    fields_to_track = [
        'date', 'poa_name', 'poa_contact', 'allergies',
        'code_status', 'relationship', 'veteran',
        'veteran_spouse', 'marital_status', 'street_address',
        'city', 'state', 'zip', 'patient_phone', 'patient_email'
    ]
    new_values = {}
    for field_name in fields_to_track:
        if hasattr(instance, field_name):
            new_values[field_name] = str(getattr(instance, field_name))
    
    AuditTrail.objects.create(
        patient=instance,
        action=action,
        record_type='PATIENT',
        user=instance.modified_by if hasattr(instance, 'modified_by') else None,
        previous_values={},
        new_values=new_values,
    )

@receiver(post_save, sender=CbcLabs)
def log_cbc_labs_save(sender, instance, created, **kwargs):
    action = 'CREATE' if created else 'UPDATE'
    AuditTrail.objects.create(
        patient=instance.patient,
        action=action,
        record_type='CBC_LAB',
        user=instance.modified_by if hasattr(instance, 'modified_by') else None,
        new_values={
            'date': str(instance.date),
            'rbc': str(instance.rbc),
            'wbc': str(instance.wbc),
            'hemoglobin': str(instance.hemoglobin),
            'hematocrit': str(instance.hematocrit),
            'mcv': str(instance.mcv),
            'mchc': str(instance.mchc),
            'rdw': str(instance.rdw),
            'platelets': str(instance.platelets),
            'mch': str(instance.mch),
            'neutrophils': str(instance.neutrophils),
            'lymphocytes': str(instance.lymphocytes),
            'monocytes': str(instance.monocytes),
            'eosinophils': str(instance.eosinophils),
            'basophils': str(instance.basophils)
        },
        previous_values={},
        
    )

@receiver(post_save, sender=CmpLabs)
def log_cmp_labs_save(sender, instance, created, **kwargs):
    action = 'CREATE' if created else 'UPDATE'
    AuditTrail.objects.create(
        patient=instance.patient,
        action=action,
        record_type='CMP_LAB',
        user=instance.modified_by if hasattr(instance, 'modified_by') else None,
        new_values={
            'date': str(instance.date),
            'sodium': str(instance.sodium),
            'potassium': str(instance.potassium),
            'chloride': str(instance.chloride),
            'co2': str(instance.co2),
            'bun': str(instance.bun),
            'creatinine': str(instance.creatinine),
            'glucose': str(instance.glucose),
            'calcium': str(instance.calcium),
            'protein': str(instance.protein),
            'albumin': str(instance.albumin),
            'bilirubin': str(instance.bilirubin)
        },
        previous_values={},
    )

@receiver(post_save, sender=Medications)
def log_medication_save(sender, instance, created, **kwargs):
    action = 'CREATE' if created else 'UPDATE'
    AuditTrail.objects.create(
        patient=instance.patient,
        action=action,
        record_type='MEDICATION',
        user=instance.modified_by if hasattr(instance, 'modified_by') else None,
        new_values={
            'date_prescribed': str(instance.date_prescribed),
            'drug': str(instance.drug),
            'dose': str(instance.dose),
            'route': str(instance.route),
            'frequency': str(instance.frequency),
            'prn': str(instance.prn),
            'dc_date': str(instance.dc_date) if instance.dc_date else None,
            'notes': str(instance.notes) if instance.notes else None
        },
        previous_values={},
    )

@receiver(post_save, sender=Diagnosis)
def log_diagnosis_save(sender, instance, created, **kwargs):
    action = 'CREATE' if created else 'UPDATE'
    AuditTrail.objects.create(
        patient=instance.patient,
        action=action,
        record_type='DIAGNOSIS',
        user=instance.modified_by if hasattr(instance, 'modified_by') else None,
        new_values={
            'date': str(instance.date),
            'diagnosis': str(instance.diagnosis),
            'icd_code': str(instance.icd_code),
            'notes': str(instance.notes) if instance.notes else None
        },
        previous_values={},
    )

@receiver(post_save, sender=ClinicalNote)
def handle_clinical_note_save(sender, instance, created, **kwargs):
    """Handle clinical note save events."""
    # Your existing signal handler code here
    pass

# VICTORY_TAG_20231118: Signal handlers disabled in favor of view-based audit trail creation
# This resolved race conditions and foreign key violations during deletions
# DO NOT REMOVE - Documents critical architectural decision

# @receiver(post_delete)
# def log_model_delete(sender, instance, **kwargs):
#     """Generic delete logger for all relevant models"""
#     # Skip if the sender is AuditTrail or not a tracked model
#     if sender == AuditTrail or not hasattr(instance, 'patient'):
#         return
        
#     # Skip if we're already handling this in the view
#     if getattr(instance, '_skip_audit_log', False):
#         return
        
#     try:
#         model_name = sender.__name__.upper()
#         # Convert instance to dict and handle serialization
#         record_dict = model_to_dict(instance)
#         for key, value in record_dict.items():
#             if isinstance(value, (datetime.date, datetime.datetime)):
#                 record_dict[key] = value.isoformat()
#             elif isinstance(value, decimal.Decimal):
#                 record_dict[key] = float(value)

#         # Handle patient deletions differently
#         if sender == Patient:
#             identifier = f"{instance.patient_number} - {instance.first_name} {instance.last_name}"
#             AuditTrail.objects.create(
#                 patient=None,  # Don't link to the patient since it's being deleted
#                 patient_identifier=identifier,
#                 action='DELETE',
#                 record_type=model_name,
#                 user=instance.modified_by if hasattr(instance, 'modified_by') else None,
#                 previous_values=record_dict
#             )
#         else:
#             AuditTrail.objects.create(
#                 patient=instance.patient,
#                 patient_identifier=f"{instance.patient.patient_number} - {instance.patient.first_name} {instance.patient.last_name}",
#                 action='DELETE',
#                 record_type=model_name,
#                 user=instance.modified_by if hasattr(instance, 'modified_by') else None,
#                 previous_values=record_dict
#             )
#     except Exception as e:
#         logger.error(f"Error creating audit trail for {sender.__name__} deletion: {str(e)}") 