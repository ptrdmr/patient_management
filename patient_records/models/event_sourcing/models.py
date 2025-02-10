import uuid
from django.db import models

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
    schema_version = models.CharField(max_length=10, default='1.0')  # For schema evolution

    class Meta:
        indexes = [
            models.Index(fields=['patient_id', 'recorded_at']),
            models.Index(fields=['event_type', 'recorded_at'])
        ]

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