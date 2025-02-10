"""Event sourcing models definition."""

from django.db import models
from ..base import BaseModel


class EventStore(BaseModel):
    """Event store for event sourcing pattern."""

    aggregate_type = models.CharField(max_length=100, help_text="Type of aggregate (e.g., PATIENT, CLINICAL)")
    aggregate_id = models.CharField(max_length=100, help_text="ID of the aggregate")
    event_type = models.CharField(max_length=100, help_text="Type of event")
    event_data = models.JSONField(help_text="Event payload data")
    metadata = models.JSONField(default=dict, help_text="Additional metadata about the event")
    sequence = models.BigIntegerField(help_text="Event sequence number", db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True, help_text="When the event occurred")

    class Meta:
        ordering = ['sequence']
        indexes = [
            models.Index(fields=['aggregate_type', 'aggregate_id']),
            models.Index(fields=['event_type']),
            models.Index(fields=['timestamp'])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['aggregate_type', 'aggregate_id', 'sequence'],
                name='unique_event_sequence'
            )
        ]

    def __str__(self):
        """Return string representation of the event."""
        return f"{self.aggregate_type} - {self.event_type} ({self.timestamp})" 