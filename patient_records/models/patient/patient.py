"""Patient model definition."""

from django.db import models
from ..base import BaseModel
from django.db.models import Max


class Patient(BaseModel):
    """Patient model representing a healthcare patient."""

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
    primary_provider = models.ForeignKey(
        'patient_records.Provider',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='primary_patients',
        help_text="Primary healthcare provider for this patient"
    )
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    emergency_contact = models.TextField()
    insurance_info = models.TextField()

    class Meta:
        indexes = [
            models.Index(fields=['patient_number']),
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['date_of_birth']),
            models.Index(fields=['phone']),
            models.Index(fields=['email']),
            models.Index(fields=['primary_provider'])
        ]

    def __str__(self):
        """Return string representation of the patient."""
        return f"{self.first_name} {self.last_name} ({self.patient_number})"

    def save(self, *args, **kwargs):
        """Override save to handle event sourcing."""
        from ..audit.events import EventStore
        from ..audit.constants import PATIENT_AGGREGATE, PATIENT_REGISTERED, PATIENT_UPDATED

        is_new = self._state.adding
        super().save(*args, **kwargs)

        # Get the next sequence number
        last_sequence = EventStore.objects.filter(
            aggregate_type=PATIENT_AGGREGATE,
            aggregate_id=str(self.id)
        ).aggregate(Max('sequence'))['sequence__max']
        
        next_sequence = (last_sequence or 0) + 1

        # Create event
        event_type = PATIENT_REGISTERED if is_new else PATIENT_UPDATED
        event_data = {
            'patient_id': str(self.id),
            'patient_number': self.patient_number,
            'name': f"{self.first_name} {self.last_name}",
            'date_of_birth': self.date_of_birth.isoformat(),
            'gender': self.gender,
            'primary_provider_id': str(self.primary_provider.id) if self.primary_provider else None
        }

        EventStore.objects.create(
            aggregate_type=PATIENT_AGGREGATE,
            aggregate_id=str(self.id),
            event_type=event_type,
            event_data=event_data,
            sequence=next_sequence
        ) 