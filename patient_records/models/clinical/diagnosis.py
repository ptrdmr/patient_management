"""Diagnosis model."""

from django.db import models
from ..base import BasePatientModel


class Diagnosis(BasePatientModel):
    """Model for patient diagnoses."""

    icd_code = models.CharField(max_length=10, help_text="ICD-10 code")
    diagnosis = models.CharField(max_length=255, help_text="Diagnosis description")
    provider = models.ForeignKey('patient_records.Provider', on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True, help_text="Additional notes about the diagnosis")
    is_active = models.BooleanField(default=True, help_text="Whether this diagnosis is currently active")
    resolved_date = models.DateField(null=True, blank=True, help_text="Date when the diagnosis was resolved")

    class Meta:
        verbose_name_plural = "diagnoses"
        indexes = [
            models.Index(fields=['icd_code']),
            models.Index(fields=['provider']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        """Return string representation of diagnosis."""
        status = "" if self.is_active else " (Resolved)"
        return f"{self.patient} - {self.diagnosis} ({self.icd_code}){status}" 