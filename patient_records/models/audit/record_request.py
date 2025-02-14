"""Record request log model definition."""

from django.db import models
from ..base import BasePatientModel


class RecordRequestLog(BasePatientModel):
    """Model for tracking record requests."""

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('COMPLETED', 'Completed'),
        ('DENIED', 'Denied'),
        ('CANCELLED', 'Cancelled')
    ]

    request_type = models.CharField(max_length=100, blank=True, null=True, help_text="Type of request")
    requester_name = models.CharField(max_length=200, blank=True, null=True, help_text="Name of person requesting records")
    requester_organization = models.CharField(max_length=200, blank=True, null=True, help_text="Organization making the request")
    purpose = models.TextField(blank=True, null=True, help_text="Purpose of the request")
    records_requested = models.TextField(blank=True, null=True, help_text="Description of requested records")
    due_date = models.DateField(blank=True, null=True, help_text="When records need to be provided")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', help_text="Current status of the request")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the request")
    needs_attention = models.BooleanField(default=False, help_text="Whether this request needs immediate attention")

    class Meta(BasePatientModel.Meta):
        verbose_name = "Record Request Log"
        verbose_name_plural = "Record Request Logs"
        indexes = [
            *BasePatientModel.Meta.indexes,
            models.Index(fields=['request_type']),
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['needs_attention'])
        ]

    def __str__(self):
        """Return string representation of the record request."""
        return f"{self.patient} - {self.request_type or 'General Request'} ({self.date})"

    def save(self, *args, **kwargs):
        """Override save to handle event creation."""
        from ...models.audit.events import EventStore
        from ...models.audit.constants import (
            CLINICAL_AGGREGATE, RECORD_REQUESTED, RECORD_REQUEST_FULFILLED,
            RECORD_REQUEST_DENIED
        )

        is_new = self._state.adding
        old_status = None if is_new else RecordRequestLog.objects.get(pk=self.pk).status

        super().save(*args, **kwargs)

        # Create appropriate event based on status changes
        if is_new:
            event_type = RECORD_REQUESTED
        elif old_status != self.status:
            if self.status == 'COMPLETED':
                event_type = RECORD_REQUEST_FULFILLED
            elif self.status == 'DENIED':
                event_type = RECORD_REQUEST_DENIED
            else:
                return  # No event for other status changes

        # Get the next sequence number
        from patient_records.management.commands.generate_test_data import Command
        sequence = Command()._get_next_sequence(CLINICAL_AGGREGATE, self.patient.id)

        # Create the event
        EventStore.objects.create(
            aggregate_type=CLINICAL_AGGREGATE,
            aggregate_id=str(self.patient.id),
            event_type=event_type,
            event_data={
                'record_request_id': str(self.id),
                'date': self.date.isoformat(),
                'request_type': self.request_type,
                'requester_name': self.requester_name,
                'requester_organization': self.requester_organization,
                'purpose': self.purpose,
                'records_requested': self.records_requested,
                'status': self.status
            },
            sequence=sequence
        ) 