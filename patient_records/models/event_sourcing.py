import uuid
from django.db import models
from django.contrib.postgres.fields import JSONField

class EventStore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    aggregate_id = models.UUIDField()
    aggregate_type = models.CharField(max_length=100)
    event_type = models.CharField(max_length=100)
    event_data = models.JSONField()
    metadata = models.JSONField(null=True)
    version = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['aggregate_id', 'version'],
                name='unique_aggregate_version'
            )
        ]
        indexes = [
            models.Index(fields=['aggregate_id', 'version']),
            models.Index(fields=['timestamp'])
        ]

class PatientReadModel(models.Model):
    id = models.UUIDField(primary_key=True)
    current_data = models.JSONField()
    last_updated = models.DateTimeField()
    version = models.IntegerField()
    snapshot_data = models.JSONField(null=True)  # For snapshotting optimization
    snapshot_version = models.IntegerField(null=True)

    class Meta:
        indexes = [
            models.Index(fields=['last_updated'])
        ]

class ClinicalReadModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    patient_id = models.UUIDField()
    event_type = models.CharField(max_length=100)
    data = models.JSONField()
    recorded_at = models.DateTimeField()
    schema_version = models.CharField(max_length=10, default='1.0')
    
    # Denormalized fields for quick access
    symptoms_summary = models.JSONField(null=True, help_text="Latest symptoms data")
    provider_details = models.JSONField(null=True, help_text="Provider information")
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['patient_id', 'recorded_at']),
            models.Index(fields=['event_type', 'recorded_at']),
            models.Index(fields=['last_updated'])
        ]
        
    def update_symptoms_summary(self, symptoms_data):
        """Update the denormalized symptoms summary"""
        if not self.symptoms_summary:
            self.symptoms_summary = {}
        self.symptoms_summary.update(symptoms_data)
        
    def update_provider_details(self, provider_data):
        """Update the denormalized provider details"""
        if not self.provider_details:
            self.provider_details = {}
        self.provider_details.update(provider_data)

class LabResultsReadModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    patient_id = models.UUIDField()
    lab_type = models.CharField(max_length=50)
    results = models.JSONField()
    performed_at = models.DateTimeField()
    schema_version = models.CharField(max_length=10, default='1.0')  # For schema evolution

    class Meta:
        indexes = [
            models.Index(fields=['patient_id', 'performed_at']),
            models.Index(fields=['lab_type', 'performed_at'])
        ] 