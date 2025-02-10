"""Base model classes and mixins."""

from django.db import models
import uuid


class BaseModel(models.Model):
    """Base model with common fields and functionality."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BasePatientModel(BaseModel):
    """Base model for all patient-related models."""

    patient = models.ForeignKey('patient.Patient', on_delete=models.CASCADE)
    source = models.CharField(max_length=100, help_text="Source system or method of data entry")
    date = models.DateField(help_text="Date of the record")

    class Meta:
        abstract = True
        ordering = ['-date']
        indexes = [
            models.Index(fields=['patient', '-date']),
            models.Index(fields=['-date']),
        ]


class BaseReadModel(models.Model):
    """Base model for read models in event sourcing pattern."""

    id = models.UUIDField(primary_key=True)
    schema_version = models.CharField(max_length=10, default='1.0')
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['last_updated'])
        ] 