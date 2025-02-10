from django.db import models
import uuid

class EventStore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    aggregate_id = models.UUIDField()
    aggregate_type = models.CharField(max_length=100)
    event_type = models.CharField(max_length=100)
    event_data = models.JSONField()
    metadata = models.JSONField(null=True)
    version = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['aggregate_id', 'version'],
                name='unique_aggregate_version'
            )
        ]
        indexes = [
            models.Index(fields=['aggregate_id', 'timestamp']),
            models.Index(fields=['aggregate_type', 'timestamp']),
            models.Index(fields=['event_type', 'timestamp'])
        ]
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.event_type} - {self.aggregate_id} - {self.timestamp}" 