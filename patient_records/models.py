"""
Patient records models.

This module provides backward compatibility by exposing all models from the new modular structure.
New code should import directly from the models package instead.
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
    ClinicalNotes,
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
    RecordRequestLog
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
    'ClinicalNotes',
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
    'RecordRequestLog'
]

from django.db import models
from django.contrib.auth.models import User
import datetime
import uuid
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from .event_sourcing.models import EventStore
from .event_sourcing.services import EventStoreService
from .event_sourcing.constants import CLINICAL_AGGREGATE, SYMPTOMS_ADDED, SYMPTOMS_UPDATED, PATIENT_AGGREGATE, PATIENT_REGISTERED, PATIENT_UPDATED
import logging

logger = logging.getLogger(__name__)

class PatientReadModel(models.Model):
    id = models.UUIDField(primary_key=True)
    current_data = models.JSONField()
    last_updated = models.DateTimeField()
    version = models.IntegerField()
    snapshot_data = models.JSONField(null=True)
    snapshot_version = models.IntegerField(null=True)

    class Meta:
        indexes = [
            models.Index(fields=['last_updated'])
        ]

class ClinicalReadModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    patient_id = models.UUIDField()
    event_type = models.CharField(max_length=100)
    data = models.JSONField()
    recorded_at = models.DateTimeField()
    schema_version = models.CharField(max_length=10, default='1.0')
    
    # Denormalized fields for quick access
    symptoms_summary = models.JSONField(null=True, help_text="Latest symptoms data")
    provider_details = models.JSONField(null=True, help_text="Provider information")
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['patient_id', 'recorded_at']),
            models.Index(fields=['event_type', 'recorded_at']),
            models.Index(fields=['last_updated'])
        ]
        
    def update_symptoms_summary(self, symptoms_data):
        """Update the denormalized symptoms summary"""
        if not self.symptoms_summary:
            self.symptoms_summary = {}
        self.symptoms_summary.update(symptoms_data)
        
    def update_provider_details(self, provider_data):
        """Update the denormalized provider details"""
        if not self.provider_details:
            self.provider_details = {}
        self.provider_details.update(provider_data)

class LabResultsReadModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    patient_id = models.UUIDField()
    lab_type = models.CharField(max_length=50)
    results = models.JSONField()
    performed_at = models.DateTimeField()
    schema_version = models.CharField(max_length=10, default='1.0')

    class Meta:
        indexes = [
            models.Index(fields=['patient_id', 'performed_at']),
            models.Index(fields=['lab_type', 'performed_at'])
        ]

# Existing Models
class Provider(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    registration_date = models.DateField(
        help_text="Date when provider was registered in the system",
        default=datetime.date.today
    )
    provider = models.CharField(max_length=100, help_text="Provider's full name")
    practice = models.CharField(max_length=200, help_text="Name of the medical practice")
    address = models.CharField(max_length=255, help_text="Street address")
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2, help_text="Two-letter US state code")
    zip_code = models.CharField(max_length=10, help_text="US ZIP code (5 or 9 digits)")
    fax = models.CharField(max_length=20, blank=True, null=True, help_text="Format: XXX-XXX-XXXX")
    phone = models.CharField(max_length=20, help_text="Format: XXX-XXX-XXXX")
    source = models.CharField(max_length=100, blank=True, null=True, help_text="Data source system")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Whether the provider is currently active")

    class Meta:
        indexes = [
            models.Index(fields=['provider']),
            models.Index(fields=['practice']),
            models.Index(fields=['-registration_date']),
            models.Index(fields=['state']),
            models.Index(fields=['is_active'])
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(state__regex=r'^[A-Z]{2}$'),
                name='valid_state_code'
            ),
            models.CheckConstraint(
                check=models.Q(zip_code__regex=r'^\d{5}(-\d{4})?$'),
                name='valid_zip_code'
            ),
            models.CheckConstraint(
                check=models.Q(phone__regex=r'^\d{3}-\d{3}-\d{4}$'),
                name='valid_phone'
            ),
            models.CheckConstraint(
                check=models.Q(fax__isnull=True) | models.Q(fax__regex=r'^\d{3}-\d{3}-\d{4}$'),
                name='valid_fax'
            )
        ]

    def clean(self):
        # Normalize state to uppercase
        if self.state:
            self.state = self.state.upper()
        
        # Format phone number if not already formatted
        if self.phone and '-' not in self.phone:
            cleaned = ''.join(filter(str.isdigit, self.phone))
            if len(cleaned) == 10:
                self.phone = f"{cleaned[:3]}-{cleaned[3:6]}-{cleaned[6:]}"
            else:
                raise ValidationError({'phone': 'Phone number must be 10 digits'})
        
        # Format fax if provided and not already formatted
        if self.fax and '-' not in self.fax:
            cleaned = ''.join(filter(str.isdigit, self.fax))
            if len(cleaned) == 10:
                self.fax = f"{cleaned[:3]}-{cleaned[3:6]}-{cleaned[6:]}"
            else:
                raise ValidationError({'fax': 'Fax number must be 10 digits'})
        
        # Format ZIP code if not already formatted
        if self.zip_code and '-' not in self.zip_code:
            cleaned = ''.join(filter(str.isdigit, self.zip_code))
            if len(cleaned) == 5:
                self.zip_code = cleaned
            elif len(cleaned) == 9:
                self.zip_code = f"{cleaned[:5]}-{cleaned[5:]}"
            else:
                raise ValidationError({'zip_code': 'ZIP code must be 5 or 9 digits'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.provider} ({self.practice})"

class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_number = models.CharField(max_length=50, unique=True, help_text="External patient identifier")
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('N', 'Prefer not to say')
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    emergency_contact = models.TextField()
    insurance_info = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['patient_number']),
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['date_of_birth'])
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.patient_number})"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        
        # Create or update the read model
        patient_data = {
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'emergency_contact': self.emergency_contact,
            'insurance_info': self.insurance_info,
            'patient_number': self.patient_number,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

        try:
            if is_new:
                event_type = 'patient_created'
                event_data = {
                    'patient_data': patient_data
                }
            else:
                event_type = 'patient_updated'
                event_data = {
                    'patient_data': patient_data
                }

            # Save the model first to get the ID if it's new
            super().save(*args, **kwargs)

            # Now we can safely use self.id
            event_store = EventStoreService()
            event_store.append_event(
                aggregate_id=str(self.id),
                aggregate_type='patient',
                event_type=event_type,
                event_data=event_data
            )

            # Create or update the read model
            try:
                read_model = PatientReadModel.objects.get(id=self.id)
                read_model.current_data = patient_data
                read_model.last_updated = timezone.now()
                read_model.version += 1
                read_model.save()
            except PatientReadModel.DoesNotExist:
                PatientReadModel.objects.create(
                    id=self.id,
                    current_data=patient_data,
                    last_updated=timezone.now(),
                    version=1
                )

        except Exception as e:
            logger.error(f"Error saving patient record: {str(e)}", 
                        extra={
                            'path': __file__,
                            'function': 'save',
                            'details': f'Error saving patient record: {str(e)}'
                        })
            raise

class Diagnosis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    icd_code = models.CharField(max_length=10)
    diagnosis = models.CharField(max_length=255)
    date = models.DateField()
    provider = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True)
    source = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "diagnoses"
        ordering = ['-date']
        indexes = [
            models.Index(fields=['patient', '-date']),
            models.Index(fields=['icd_code'])
        ]

    def __str__(self):
        return f"{self.icd_code} - {self.diagnosis}"

class Visits(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    visit_type = models.CharField(max_length=100)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    practice = models.CharField(max_length=200)
    chief_complaint = models.TextField(blank=True, null=True)
    assessment = models.TextField(blank=True, null=True)
    plan = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True)
    source = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "visits"
        ordering = ['-date']
        indexes = [
            models.Index(fields=['patient', '-date']),
            models.Index(fields=['visit_type'])
        ]

    def __str__(self):
        return f"{self.visit_type} - {self.date}"

class Symptoms(models.Model):
    SEVERITY_CHOICES = [
        (1, '1 - Minimal'),
        (2, '2 - Mild'),
        (3, '3 - Moderate'),
        (4, '4 - Severe'),
        (5, '5 - Very Severe')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='symptoms')
    date = models.DateField(help_text="Date when symptom was reported")
    symptom = models.CharField(max_length=200, help_text="Primary symptom description")
    severity = models.IntegerField(choices=SEVERITY_CHOICES, null=True, blank=True, help_text="Severity level of symptom")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the symptom")
    source = models.CharField(max_length=100, help_text="Source of symptom information")
    person_reporting = models.CharField(max_length=200, help_text="Person who reported the symptom")
    provider = models.ForeignKey(
        Provider, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Healthcare provider associated with this symptom"
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Symptom'
        verbose_name_plural = 'Symptoms'
        ordering = ['-date', '-last_updated']
        indexes = [
            models.Index(fields=['patient', '-date']),
            models.Index(fields=['symptom']),
            models.Index(fields=['-last_updated'])
        ]

    def __str__(self):
        return f"{self.symptom} - {self.date}"

    def clean(self):
        """Validate the model data"""
        if self.severity and (self.severity < 1 or self.severity > 5):
            raise ValidationError({
                'severity': 'Severity must be between 1 and 5'
            })
        
        if self.date and self.date > timezone.now().date():
            raise ValidationError({
                'date': 'Date cannot be in the future'
            })

    def save(self, *args, **kwargs):
        """Override save to ensure proper data handling"""
        self.full_clean()
        
        # Ensure proper string formatting
        self.symptom = self.symptom.strip()
        if self.notes:
            self.notes = self.notes.strip()
        
        # Create event store entry
        try:
            with transaction.atomic():
                super().save(*args, **kwargs)
                
                event_store = EventStoreService()
                
                event_data = {
                    'patient_id': str(self.patient.id),  # Patient ID is already a UUID
                    'symptoms_id': str(self.id),
                    'date': self.date.isoformat(),
                    'symptom': self.symptom,
                    'severity': self.severity,
                    'notes': self.notes,
                    'source': self.source,
                    'person_reporting': self.person_reporting,
                    'provider_id': str(self.provider.id) if self.provider else None
                }
                
                event_store.append_event(
                    aggregate_id=str(self.patient.id),  # Patient ID is already a UUID
                    aggregate_type=CLINICAL_AGGREGATE,
                    event_type=SYMPTOMS_ADDED if not self.pk else SYMPTOMS_UPDATED,
                    event_data=event_data
                )
        except Exception as e:
            logger.error(f"Error saving symptom record: {str(e)}")
            raise

    @property
    def severity_display(self):
        """Return human-readable severity"""
        if self.severity:
            return dict(self.SEVERITY_CHOICES).get(self.severity, 'Unknown')
        return 'Not Assessed'

class Medications(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date_prescribed = models.DateField()
    drug = models.CharField(max_length=200)
    dose = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    route = models.CharField(max_length=100)
    notes = models.TextField(blank=True, null=True)
    prn = models.BooleanField(default=False, verbose_name="PRN (As Needed)")
    dc_date = models.DateField(null=True, blank=True, verbose_name="Discontinue Date")

    class Meta:
        indexes = [
            models.Index(fields=['-date_prescribed']),
            models.Index(fields=['patient', '-date_prescribed']),
        ]
        ordering = ['-date_prescribed']

    def clean(self):
        """Validate the model data."""
        if self.dc_date and self.dc_date < self.date_prescribed:
            raise ValidationError({
                'dc_date': 'Discontinue date cannot be earlier than the prescribed date.'
            })

    def save(self, *args, **kwargs):
        """Override save to ensure validation is called."""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.drug} - {self.dose}"

class Measurements(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    weight = models.FloatField()
    value = models.FloatField(null=True, blank=True)
    source = models.CharField(max_length=100)
    nutritional_intake = models.CharField(max_length=200)
    mac = models.CharField(max_length=100)
    fast = models.CharField(max_length=100)
    pps = models.CharField(max_length=100)
    plof = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "measurements"
        ordering = ['-date']
        indexes = [
            models.Index(fields=['patient', '-date'])
        ]

    def __str__(self):
        return f"Measurements - {self.patient} - {self.date}"

class Imaging(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    type = models.CharField(max_length=100)
    body_part = models.CharField(max_length=100, blank=True, null=True)
    findings = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True)
    source = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "imaging"
        ordering = ['-date']
        indexes = [
            models.Index(fields=['patient', '-date']),
            models.Index(fields=['type'])
        ]

    def __str__(self):
        return f"{self.type} - {self.patient} - {self.date}"

class Adls(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    ambulation = models.CharField(max_length=100)
    continence = models.CharField(max_length=100)
    transfer = models.CharField(max_length=100)
    toileting = models.CharField(max_length=100, blank=True, null=True)
    transferring = models.CharField(max_length=100, blank=True, null=True)
    dressing = models.CharField(max_length=100)
    feeding = models.CharField(max_length=100)
    bathing = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    source = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'ADL'
        verbose_name_plural = 'ADLs'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['patient', '-date'])
        ]

    def __str__(self):
        return f"ADLs - {self.patient} - {self.date}"

class Occurrences(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    occurrence_type = models.CharField(max_length=100)
    description = models.TextField()
    action_taken = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True)
    source = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "occurrences"
        ordering = ['-date']
        indexes = [
            models.Index(fields=['patient', '-date']),
            models.Index(fields=['occurrence_type'])
        ]

    def __str__(self):
        return f"{self.occurrence_type} - {self.patient} - {self.date}"

class RecordRequestLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    request_type = models.CharField(max_length=100, blank=True, null=True)
    purpose = models.TextField(blank=True, null=True)
    records_requested = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Record Request Log"
        verbose_name_plural = "Record Request Logs"
        ordering = ['-date']
        indexes = [
            models.Index(fields=['patient', '-date']),
            models.Index(fields=['request_type'])
        ]

    def __str__(self):
        return f"Record Request - {self.patient} - {self.date}"

class AuditTrail(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.SET_NULL, null=True)
    patient_identifier = models.CharField(max_length=100, default="Unknown Patient")
    action = models.CharField(
        max_length=10,
        choices=[('CREATE', 'Create'), ('UPDATE', 'Update'), ('DELETE', 'Delete')]
    )
    record_type = models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    previous_values = models.JSONField(default=dict)
    new_values = models.JSONField(default=dict)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['patient_identifier', '-timestamp']),
            models.Index(fields=['action', '-timestamp'])
        ]

    def __str__(self):
        return f"{self.action} {self.record_type} - {self.patient_identifier or 'Unknown'}"

    def save(self, *args, **kwargs):
        # Ensure patient_identifier is set even if patient is null
        if not self.patient_identifier and self.patient:
            self.patient_identifier = f"{self.patient.patient_number} - {self.patient.first_name} {self.patient.last_name}"
        super().save(*args, **kwargs)

# Add this model after your existing models
class ClinicalNotes(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    provider = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True)
    notes = models.TextField()
    source = models.CharField(max_length=100, default='manual')
    
    class Meta:
        ordering = ['-date']
        verbose_name = 'Clinical Note'
        verbose_name_plural = 'Clinical Notes'
        indexes = [
            models.Index(fields=['-date']),
            models.Index(fields=['patient', '-date']),
        ]

    def __str__(self):
        return f"Clinical Note - {self.patient} - {self.date}"

class NoteTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class PatientNote(models.Model):
    NOTE_CATEGORIES = [
        ('OVERVIEW', 'Overview'),
        ('CLINICAL', 'Clinical Data'),
        ('VISITS', 'Visits'),
        ('MEDICATIONS', 'Medications'),
        ('LABS', 'Lab Results'),
        ('VITALS', 'Vital Signs'),
        ('GENERAL', 'General Notes'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=NOTE_CATEGORIES, default='GENERAL')
    tags = models.ManyToManyField(NoteTag, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_pinned = models.BooleanField(default=False)
    
    # Reference to any patient record
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.CharField(max_length=100, null=True, blank=True)
    referenced_record = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-is_pinned', '-created_at']
        indexes = [
            models.Index(fields=['patient', '-created_at']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.title} - {self.patient}"

    @property
    def short_content(self):
        """Return truncated content for preview"""
        return self.content[:150] + '...' if len(self.content) > 150 else self.content

class NoteAttachment(models.Model):
    note = models.ForeignKey(PatientNote, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='note_attachments/%Y/%m/%d/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_type = models.CharField(max_length=50)

    def __str__(self):
        return self.filename

    def save(self, *args, **kwargs):
        if not self.filename:
            self.filename = self.file.name
        super().save(*args, **kwargs)

