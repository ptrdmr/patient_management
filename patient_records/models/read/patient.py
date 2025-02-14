"""Patient read models."""

from django.db import models
from ..base import BaseReadModel

class PatientReadModel(BaseReadModel):
    """Read model for patient data."""
    
    current_data = models.JSONField(help_text="Current state of patient data")
    version = models.IntegerField(help_text="Version of the patient data")
    snapshot_data = models.JSONField(
        null=True,
        help_text="Snapshot of patient data at a point in time"
    )
    snapshot_version = models.IntegerField(
        null=True,
        help_text="Version of the snapshot data"
    )
    
    class Meta(BaseReadModel.Meta):
        indexes = [
            *BaseReadModel.Meta.indexes
        ]
        
    def __str__(self):
        """Return string representation of the patient read model."""
        return f"Patient {self.id} - Version {self.version}" 