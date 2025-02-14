"""Medications model."""

from django.db import models
from ..base import BasePatientModel


class Medications(BasePatientModel):
    """Model for patient medications."""

    ROUTE_CHOICES = [
        ('PO', 'Oral'),
        ('IV', 'Intravenous'),
        ('IM', 'Intramuscular'),
        ('SC', 'Subcutaneous'),
        ('TD', 'Transdermal'),
        ('INH', 'Inhalation'),
        ('TOP', 'Topical'),
        ('SL', 'Sublingual'),
        ('PR', 'Per Rectum'),
        ('OTH', 'Other')
    ]

    drug = models.CharField(max_length=255, help_text="Name of the medication")
    dose = models.CharField(max_length=100, help_text="Dose of the medication")
    route = models.CharField(max_length=50, help_text="Route of administration")
    frequency = models.CharField(max_length=100, help_text="How often to take the medication")
    date_prescribed = models.DateField(help_text="Date the medication was prescribed")
    dc_date = models.DateField(null=True, blank=True, help_text="Date the medication was discontinued")
    provider = models.ForeignKey('patient_records.Provider', on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True, help_text="Additional notes about the medication")
    prn = models.BooleanField(default=False, help_text="Whether this is an as-needed medication")

    class Meta:
        verbose_name_plural = "medications"
        indexes = [
            models.Index(fields=['drug']),
            models.Index(fields=['provider']),
            models.Index(fields=['date_prescribed']),
            models.Index(fields=['dc_date']),
        ]

    def __str__(self):
        """Return string representation of medication."""
        status = " (Discontinued)" if self.dc_date else ""
        return f"{self.drug} {self.dose}{status}"

    @property
    def is_active(self):
        """Return whether medication is currently active."""
        return self.dc_date is None 