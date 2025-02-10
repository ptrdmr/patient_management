"""Clinical notes models."""

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from ..base import BasePatientModel


class NoteTag(models.Model):
    """Model for categorizing and organizing notes."""

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return string representation of tag."""
        return self.name


class PatientNote(BasePatientModel):
    """Model for general patient notes."""

    NOTE_CATEGORIES = [
        ('OVERVIEW', 'Overview'),
        ('CLINICAL', 'Clinical Data'),
        ('VISITS', 'Visits'),
        ('MEDICATIONS', 'Medications'),
        ('LABS', 'Lab Results'),
        ('VITALS', 'Vital Signs'),
        ('GENERAL', 'General Notes'),
    ]

    title = models.CharField(max_length=200, help_text="Title of the note")
    content = models.TextField(help_text="Note content")
    category = models.CharField(
        max_length=20,
        choices=NOTE_CATEGORIES,
        default='GENERAL',
        help_text="Category of note"
    )
    tags = models.ManyToManyField(NoteTag, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text="User who created the note"
    )
    is_pinned = models.BooleanField(
        default=False,
        help_text="Whether this note is pinned"
    )

    # Reference to any patient record
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.CharField(max_length=100, null=True, blank=True)
    referenced_record = GenericForeignKey('content_type', 'object_id')

    class Meta(BasePatientModel.Meta):
        ordering = ['-is_pinned', '-created_at']
        indexes = [
            *BasePatientModel.Meta.indexes,
            models.Index(fields=['category']),
            models.Index(fields=['created_by']),
            models.Index(fields=['is_pinned'])
        ]

    def __str__(self):
        """Return string representation of note."""
        return f"{self.title} - {self.patient}"

    @property
    def short_content(self):
        """Return truncated content for preview."""
        return self.content[:150] + '...' if len(self.content) > 150 else self.content


class ClinicalNote(BasePatientModel):
    """Model for clinical/medical notes."""

    provider = models.ForeignKey(
        'patient_records.Provider',
        on_delete=models.SET_NULL,
        null=True,
        help_text="Provider who wrote the note"
    )
    content = models.TextField(help_text="Clinical note content")
    source = models.CharField(
        max_length=100,
        default='manual',
        help_text="Source of the note"
    )

    class Meta(BasePatientModel.Meta):
        ordering = ['-date']
        indexes = [
            *BasePatientModel.Meta.indexes,
            models.Index(fields=['provider']),
            models.Index(fields=['source'])
        ]

    def __str__(self):
        """Return string representation of clinical note."""
        return f"Clinical Note - {self.patient} - {self.date}"


class NoteAttachment(models.Model):
    """Model for file attachments to notes."""

    note = models.ForeignKey(
        PatientNote,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(
        upload_to='note_attachments/%Y/%m/%d/',
        help_text="Attached file"
    )
    filename = models.CharField(max_length=255, help_text="Original filename")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_type = models.CharField(max_length=50, help_text="Type of file")

    def __str__(self):
        """Return string representation of attachment."""
        return self.filename

    def save(self, *args, **kwargs):
        """Override save to ensure filename is set."""
        if not self.filename:
            self.filename = self.file.name
        super().save(*args, **kwargs) 