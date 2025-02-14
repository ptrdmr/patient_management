"""Audit trail model definition."""

from django.db import models
from django.contrib.auth.models import User
from ..base import BaseModel


class AuditTrail(BaseModel):
    """Model for tracking changes to patient records."""

    patient = models.ForeignKey('patient_records.Patient', on_delete=models.SET_NULL, null=True)
    patient_identifier = models.CharField(max_length=100, default="Unknown Patient")
    action = models.CharField(
        max_length=10,
        choices=[('CREATE', 'Create'), ('UPDATE', 'Update'), ('DELETE', 'Delete')]
    )
    record_type = models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    previous_values = models.JSONField(default=dict)
    new_values = models.JSONField(default=dict)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['patient']),
            models.Index(fields=['action']),
            models.Index(fields=['record_type']),
            models.Index(fields=['user']),
            models.Index(fields=['-timestamp'])
        ]

    def __str__(self):
        """Return string representation of the audit trail entry."""
        return f"{self.action} {self.record_type} for {self.patient_identifier}"

    def save(self, *args, **kwargs):
        """Override save to ensure patient_identifier is set."""
        # Ensure patient_identifier is set even if patient is null
        if self.patient and not self.patient_identifier:
            self.patient_identifier = f"{self.patient.first_name} {self.patient.last_name} ({self.patient.patient_number})"
        super().save(*args, **kwargs) 