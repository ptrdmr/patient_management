"""Imaging model definition."""

from django.db import models
from ..base import BasePatientModel


class Imaging(BasePatientModel):
    """Model for tracking patient imaging studies."""

    type = models.CharField(max_length=100, help_text="Type of imaging study")
    body_part = models.CharField(max_length=100, blank=True, null=True, help_text="Body part imaged")
    findings = models.TextField(blank=True, null=True, help_text="Imaging findings")
    notes = models.TextField(blank=True, help_text="Additional notes about the imaging")

    class Meta(BasePatientModel.Meta):
        verbose_name_plural = "imaging"
        indexes = [
            *BasePatientModel.Meta.indexes,
            models.Index(fields=['type']),
            models.Index(fields=['body_part'])
        ]

    def __str__(self):
        """Return string representation of imaging study."""
        body_part_str = f" - {self.body_part}" if self.body_part else ""
        return f"{self.patient} - {self.type}{body_part_str} ({self.date})" 