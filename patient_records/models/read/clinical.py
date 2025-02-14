"""Clinical read models."""

from django.db import models
import uuid
from ..base import BaseReadModel

class ClinicalReadModel(BaseReadModel):
    """Read model for clinical events and data."""
    
    patient_id = models.UUIDField(help_text="ID of the patient this data belongs to")
    event_type = models.CharField(max_length=100, help_text="Type of clinical event")
    data = models.JSONField(help_text="Clinical event data")
    recorded_at = models.DateTimeField(help_text="When the event was recorded")
    
    # Denormalized fields for quick access
    symptoms_summary = models.JSONField(
        null=True,
        help_text="Latest symptoms data"
    )
    provider_details = models.JSONField(
        null=True,
        help_text="Provider information"
    )
    
    class Meta(BaseReadModel.Meta):
        indexes = [
            *BaseReadModel.Meta.indexes,
            models.Index(fields=['patient_id', 'recorded_at']),
            models.Index(fields=['event_type', 'recorded_at'])
        ]
        
    def __str__(self):
        """Return string representation of the clinical read model."""
        return f"{self.event_type} - Patient {self.patient_id} ({self.recorded_at})" 