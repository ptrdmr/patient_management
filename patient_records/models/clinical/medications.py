"""Medications model definition."""

from django.db import models
from ..base import BasePatientModel


class Medications(BasePatientModel):
    """Model for tracking patient medications."""

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

    drug = models.CharField(max_length=200, help_text="Name of medication")
    dose = models.CharField(max_length=100, help_text="Dosage amount")
    route = models.CharField(
        max_length=3,
        choices=ROUTE_CHOICES,
        help_text="Route of administration"
    )
    frequency = models.CharField(max_length=100, help_text="How often to take")
    date_prescribed = models.DateField(help_text="When the medication was prescribed")
    dc_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date medication was discontinued"
    )
    provider = models.ForeignKey(
        'patient.Provider',
        on_delete=models.SET_NULL,
        null=True,
        help_text="Provider who prescribed the medication"
    )
    prn = models.BooleanField(default=False, help_text="Whether medication is as-needed")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about medication")

    class Meta(BasePatientModel.Meta):
        verbose_name = 'Medication'
        verbose_name_plural = 'Medications'
        indexes = [
            *BasePatientModel.Meta.indexes,
            models.Index(fields=['drug']),
            models.Index(fields=['provider']),
            models.Index(fields=['date_prescribed']),
            models.Index(fields=['dc_date'])
        ]

    def __str__(self):
        """Return string representation of medication."""
        status = " (Discontinued)" if self.dc_date else ""
        return f"{self.patient} - {self.drug} {self.dose}{status}"

    @property
    def is_active(self):
        """Return whether medication is currently active."""
        return self.dc_date is None 