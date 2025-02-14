"""Lab results read models."""

from django.db import models
from ..base import BaseReadModel

class LabResultsReadModel(BaseReadModel):
    """Read model for lab results data."""
    
    patient_id = models.UUIDField(help_text="ID of the patient this data belongs to")
    lab_type = models.CharField(max_length=50, help_text="Type of lab test")
    results = models.JSONField(help_text="Lab test results data")
    performed_at = models.DateTimeField(help_text="When the lab test was performed")
    schema_version = models.CharField(
        max_length=10,
        default='1.0',
        help_text="Version of the data schema"
    )
    
    class Meta(BaseReadModel.Meta):
        indexes = [
            *BaseReadModel.Meta.indexes,
            models.Index(fields=['patient_id', 'performed_at']),
            models.Index(fields=['lab_type', 'performed_at'])
        ]
        
    def __str__(self):
        """Return string representation of the lab results read model."""
        return f"{self.lab_type} - Patient {self.patient_id} ({self.performed_at})" 