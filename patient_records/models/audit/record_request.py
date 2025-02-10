"""Record request log model definition."""

from django.db import models
from ..base import BasePatientModel


class RecordRequestLog(BasePatientModel):
    """Model for tracking record requests."""

    request_type = models.CharField(max_length=100, blank=True, null=True, help_text="Type of request")
    purpose = models.TextField(blank=True, null=True, help_text="Purpose of the request")
    records_requested = models.TextField(blank=True, null=True, help_text="Description of requested records")

    class Meta(BasePatientModel.Meta):
        verbose_name = "Record Request Log"
        verbose_name_plural = "Record Request Logs"
        indexes = [
            *BasePatientModel.Meta.indexes,
            models.Index(fields=['request_type'])
        ]

    def __str__(self):
        """Return string representation of the record request."""
        return f"{self.patient} - {self.request_type or 'General Request'} ({self.date})" 