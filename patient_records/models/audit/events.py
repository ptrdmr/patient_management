"""Event sourcing models definition."""

from django.db import models
from django.core.exceptions import ValidationError
from ..base import BaseModel


class EventStore(BaseModel):
    """Event store for event sourcing pattern."""

    aggregate_type = models.CharField(max_length=100, help_text="Type of aggregate (e.g., PATIENT, CLINICAL)")
    aggregate_id = models.CharField(max_length=100, help_text="ID of the aggregate")
    event_type = models.CharField(max_length=100, help_text="Type of event")
    event_data = models.JSONField(help_text="Event payload data")
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional metadata about the event")
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

    def clean(self):
        """Validate the event store entry."""
        super().clean()
        
        if self.sequence is not None:
            # Check if sequence is positive
            if self.sequence < 1:
                raise ValidationError({
                    'sequence': 'Sequence number must be positive'
                })
            
            # Get the highest sequence number for this aggregate
            highest_sequence = EventStore.objects.filter(
                aggregate_type=self.aggregate_type,
                aggregate_id=self.aggregate_id
            ).order_by('-sequence').values_list('sequence', flat=True).first()
            
            # For new records, ensure sequence is consecutive
            if highest_sequence is None:
                # First event must have sequence 1
                if self.sequence != 1:
                    raise ValidationError({
                        'sequence': 'First event must have sequence number 1'
                    })
            else:
                # Next event must be consecutive
                if self.sequence != highest_sequence + 1:
                    raise ValidationError({
                        'sequence': 'Sequence numbers must be consecutive'
                    })

    def save(self, *args, **kwargs):
        """Override save to ensure clean is called."""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """Return string representation of the event."""
        return f"{self.aggregate_type} - {self.event_type} ({self.timestamp})" 