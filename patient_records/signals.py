from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Patient, AuditTrail

@receiver(post_save, sender=Patient)
def log_patient_save(sender, instance, created, **kwargs):
    action = 'CREATE' if created else 'UPDATE'
    
    # Explicitly list the fields we want to track
    fields_to_track = [
        'date',
        'poa_name',
        'poa_contact',
        'allergies',
        'code_status',
        'relationship',
        'veteran',
        'veteran_spouse',
        'marital_status',
        'street_address',
        'city',
        'state',
        'zip',
        'patient_phone',
        'patient_email'
    ]
    
    # Create new_values dictionary
    new_values = {}
    for field_name in fields_to_track:
        if hasattr(instance, field_name):
            new_values[field_name] = str(getattr(instance, field_name))
    
    AuditTrail.objects.create(
        patient=instance, 
        action=action,
        record_type='PATIENT',  # Added required field
        user=instance.modified_by,
        previous_values={},  # Empty for now, could track actual changes later
        new_values=new_values,
        ip_address=None  # Required field, but can be null
    )

@receiver(post_delete, sender=Patient)
def log_patient_delete(sender, instance, **kwargs):
    AuditTrail.objects.create(
        patient=instance, 
        action='DELETE',
        record_type='PATIENT',  # Added required field
        user=instance.modified_by,
        previous_values={},
        new_values={},
        ip_address=None  # Required field, but can be null
    ) 