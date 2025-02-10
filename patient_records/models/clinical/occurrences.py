"""Occurrences model definition."""

from django.db import models
from ..base import BasePatientModel


class Occurrences(BasePatientModel):
    """Model for tracking patient occurrences and incidents."""

    occurrence_type = models.CharField(max_length=100, help_text="Type of occurrence")
    description = models.TextField(help_text="Detailed description of the occurrence")
    action_taken = models.TextField(blank=True, null=True, help_text="Actions taken in response")
    notes = models.TextField(blank=True, help_text="Additional notes about the occurrence")

    class Meta(BasePatientModel.Meta):
        verbose_name_plural = "occurrences"
        indexes = [
            *BasePatientModel.Meta.indexes,
            models.Index(fields=['occurrence_type'])
        ]

    def __str__(self):
        """Return string representation of occurrence."""
        return f"{self.patient} - {self.occurrence_type} ({self.date})" 