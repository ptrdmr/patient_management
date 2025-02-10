"""Diagnosis model definition."""

from django.db import models
from ..base import BasePatientModel


class Diagnosis(BasePatientModel):
    """Model for tracking patient diagnoses."""

    icd_code = models.CharField(max_length=10, help_text="ICD-10 diagnosis code")
    diagnosis = models.CharField(max_length=200, help_text="Diagnosis description")
    provider = models.ForeignKey(
        'patient.Provider',
        on_delete=models.SET_NULL,
        null=True,
        help_text="Provider who made the diagnosis"
    )
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the diagnosis")
    is_active = models.BooleanField(default=True, help_text="Whether this diagnosis is currently active")
    resolved_date = models.DateField(null=True, blank=True, help_text="Date when the diagnosis was resolved")

    class Meta(BasePatientModel.Meta):
        verbose_name_plural = "diagnoses"
        indexes = [
            *BasePatientModel.Meta.indexes,
            models.Index(fields=['icd_code']),
            models.Index(fields=['provider']),
            models.Index(fields=['is_active'])
        ]

    def __str__(self):
        """Return string representation of diagnosis."""
        status = "" if self.is_active else " (Resolved)"
        return f"{self.patient} - {self.diagnosis} ({self.icd_code}){status}" 