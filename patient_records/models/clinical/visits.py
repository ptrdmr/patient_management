"""Visits model definition."""

from django.db import models
from ..base import BasePatientModel


class Visits(BasePatientModel):
    """Model for tracking patient visits."""

    VISIT_TYPES = [
        ('OFFICE', 'Office Visit'),
        ('HOME', 'Home Visit'),
        ('VIRTUAL', 'Virtual Visit'),
        ('HOSPITAL', 'Hospital Visit'),
        ('EMERGENCY', 'Emergency Visit'),
        ('FOLLOWUP', 'Follow-up Visit')
    ]

    visit_type = models.CharField(
        max_length=20,
        choices=VISIT_TYPES,
        help_text="Type of visit"
    )
    provider = models.ForeignKey(
        'patient_records.Provider',
        on_delete=models.SET_NULL,
        null=True,
        help_text="Provider who conducted the visit"
    )
    practice = models.CharField(max_length=200, help_text="Practice/facility where visit occurred")
    chief_complaint = models.TextField(blank=True, null=True, help_text="Primary reason for visit")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the visit")
    follow_up_needed = models.BooleanField(default=False, help_text="Whether follow-up is needed")
    follow_up_date = models.DateField(null=True, blank=True, help_text="Recommended follow-up date")

    class Meta(BasePatientModel.Meta):
        verbose_name = 'Visit'
        verbose_name_plural = 'Visits'
        indexes = [
            *BasePatientModel.Meta.indexes,
            models.Index(fields=['visit_type']),
            models.Index(fields=['provider']),
            models.Index(fields=['practice']),
            models.Index(fields=['follow_up_needed'])
        ]

    def __str__(self):
        """Return string representation of visit."""
        return f"{self.patient} - {self.get_visit_type_display()} ({self.date})" 