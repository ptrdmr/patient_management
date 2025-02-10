"""Vitals model definition."""

from django.db import models
from ..base import BasePatientModel


class Vitals(BasePatientModel):
    """Model for tracking patient vital signs."""

    blood_pressure = models.CharField(max_length=20)
    temperature = models.FloatField()
    spo2 = models.FloatField()
    pulse = models.IntegerField()
    respirations = models.IntegerField()
    supp_o2 = models.BooleanField(default=False)
    pain = models.IntegerField()

    class Meta(BasePatientModel.Meta):
        verbose_name_plural = "vitals"
        indexes = [
            *BasePatientModel.Meta.indexes,
            models.Index(fields=['blood_pressure']),
            models.Index(fields=['temperature']),
            models.Index(fields=['spo2']),
            models.Index(fields=['pulse']),
            models.Index(fields=['pain'])
        ]

    def __str__(self):
        """Return string representation of vitals."""
        return f"{self.patient} - BP: {self.blood_pressure}, Temp: {self.temperature}°F, SpO2: {self.spo2}% ({self.date})" 