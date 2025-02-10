"""Activities of Daily Living (ADLs) model definition."""

from django.db import models
from ..base import BasePatientModel


class Adls(BasePatientModel):
    """Model for tracking patient Activities of Daily Living (ADLs)."""

    ambulation = models.CharField(max_length=100, help_text="Patient's ability to walk/move around")
    continence = models.CharField(max_length=100, help_text="Patient's bladder/bowel control")
    transfer = models.CharField(max_length=100, help_text="Patient's ability to transfer between surfaces")
    toileting = models.CharField(max_length=100, blank=True, null=True, help_text="Patient's ability to use toilet")
    transferring = models.CharField(max_length=100, blank=True, null=True, help_text="Patient's ability to transfer")
    dressing = models.CharField(max_length=100, help_text="Patient's ability to dress themselves")
    feeding = models.CharField(max_length=100, help_text="Patient's ability to feed themselves")
    bathing = models.CharField(max_length=100, help_text="Patient's ability to bathe themselves")
    notes = models.TextField(blank=True, help_text="Additional notes about ADLs")

    class Meta(BasePatientModel.Meta):
        verbose_name = 'ADL'
        verbose_name_plural = 'ADLs'
        indexes = [
            *BasePatientModel.Meta.indexes,
            models.Index(fields=['ambulation']),
            models.Index(fields=['continence']),
            models.Index(fields=['feeding'])
        ]

    def __str__(self):
        """Return string representation of ADLs assessment."""
        return f"{self.patient} - ADLs Assessment ({self.date})" 