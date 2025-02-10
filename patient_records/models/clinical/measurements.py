"""Measurements model definition."""

from django.db import models
from ..base import BasePatientModel


class Measurements(BasePatientModel):
    """Model for tracking patient measurements and assessments."""

    weight = models.FloatField(help_text="Weight in pounds")
    value = models.FloatField(null=True, blank=True, help_text="Additional value measurement")
    nutritional_intake = models.CharField(max_length=200, help_text="Description of nutritional intake")
    mac = models.CharField(max_length=100, help_text="Mid-arm circumference")
    fast = models.CharField(max_length=100, help_text="Functional Assessment Screening Tool")
    pps = models.CharField(max_length=100, help_text="Palliative Performance Scale")
    plof = models.CharField(max_length=100, help_text="Prior Level of Function")

    class Meta(BasePatientModel.Meta):
        verbose_name_plural = "measurements"
        indexes = [
            *BasePatientModel.Meta.indexes,
            models.Index(fields=['weight']),
            models.Index(fields=['pps'])
        ]

    def __str__(self):
        """Return string representation of measurements."""
        return f"{self.patient} - Weight: {self.weight}lbs, PPS: {self.pps} ({self.date})" 