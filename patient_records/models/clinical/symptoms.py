"""Symptoms model definition."""

from django.db import models
from ..base import BasePatientModel


class Symptoms(BasePatientModel):
    """Model for tracking patient symptoms."""

    SEVERITY_CHOICES = [
        (1, '1 - Minimal'),
        (2, '2 - Mild'),
        (3, '3 - Moderate'),
        (4, '4 - Severe'),
        (5, '5 - Very Severe')
    ]

    symptom = models.CharField(max_length=200, help_text="Primary symptom description")
    severity = models.IntegerField(
        choices=SEVERITY_CHOICES,
        null=True,
        blank=True,
        help_text="Severity level of symptom"
    )
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the symptom")
    person_reporting = models.CharField(max_length=200, help_text="Person who reported the symptom")
    provider = models.ForeignKey(
        'patient_records.Provider',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Healthcare provider associated with this symptom"
    )

    class Meta(BasePatientModel.Meta):
        verbose_name = 'Symptom'
        verbose_name_plural = 'Symptoms'
        ordering = ['-date', '-created_at']
        indexes = [
            *BasePatientModel.Meta.indexes,
            models.Index(fields=['symptom']),
            models.Index(fields=['severity']),
            models.Index(fields=['provider'])
        ]

    def __str__(self):
        """Return string representation of the symptom."""
        severity = f" (Severity: {self.get_severity_display()})" if self.severity else ""
        return f"{self.patient} - {self.symptom}{severity} ({self.date})"

    def clean(self):
        """Clean and validate symptom data."""
        if self.severity and (self.severity < 1 or self.severity > 5):
            raise models.ValidationError({
                'severity': 'Severity must be between 1 and 5'
            })

    def _create_event(self):
        """Create event for symptom changes."""
        from ..audit.events import EventStore
        from ..audit.constants import CLINICAL_AGGREGATE, SYMPTOMS_ADDED, SYMPTOMS_UPDATED

        is_new = self._state.adding
        event_type = SYMPTOMS_ADDED if is_new else SYMPTOMS_UPDATED
        event_data = {
            'patient_id': str(self.patient.id),
            'symptom_id': str(self.id),
            'symptom': self.symptom,
            'severity': self.severity,
            'date': self.date.isoformat(),
            'provider_id': str(self.provider.id) if self.provider else None
        }

        # Get the next sequence number
        from patient_records.management.commands.generate_test_data import Command
        sequence = Command()._get_next_sequence(CLINICAL_AGGREGATE, self.patient.id)

        EventStore.objects.create(
            aggregate_type=CLINICAL_AGGREGATE,
            aggregate_id=str(self.patient.id),
            event_type=event_type,
            event_data=event_data,
            sequence=sequence
        )

    @property
    def severity_display(self):
        """Return formatted severity display."""
        return self.get_severity_display() if self.severity else "Not Specified" 