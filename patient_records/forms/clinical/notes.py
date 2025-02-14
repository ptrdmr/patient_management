"""Notes form module."""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from ...models import PatientNote, NoteAttachment, NoteTag
from ..base import SectionedMedicalForm
from ...models.audit.constants import CLINICAL_AGGREGATE

class PatientNoteForm(SectionedMedicalForm):
    """Form for patient notes with enhanced validation and safety features."""
    
    aggregate_type = CLINICAL_AGGREGATE

    # Critical note content requiring attention
    CRITICAL_CONTENT = {
        'suicide': 'Suicidal ideation - requires immediate psychiatric evaluation',
        'abuse': 'Abuse reported - requires mandatory reporting',
        'fall': 'Fall reported - requires immediate safety assessment',
        'deterioration': 'Clinical deterioration - requires immediate evaluation',
        'adverse reaction': 'Adverse reaction - requires immediate medical review',
        'error': 'Medical error - requires incident reporting'
    }
    
    class Meta:
        model = PatientNote
        fields = [
            'title',
            'content',
            'category',
            'tags',
            'date',
            'is_pinned',
            'source'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter note title'
            }),
            'content': forms.Textarea(attrs={
                'rows': 5,
                'class': 'form-control',
                'placeholder': 'Enter detailed note content'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'tags': forms.SelectMultiple(attrs={
                'class': 'form-control'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'max': timezone.now().date().isoformat(),
                'class': 'form-control'
            }),
            'source': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off'
            })
        }
        help_texts = {
            'title': 'Clear, descriptive title for the note',
            'content': 'Detailed note content - critical information will be flagged',
            'category': 'Category for organizing notes',
            'tags': 'Tags for easier searching and filtering',
            'date': 'Date this note was written',
            'is_pinned': 'Pin important notes to the top',
            'source': 'Source of note information'
        }

    def clean_content(self):
        """Clean and validate note content."""
        content = self.cleaned_data.get('content', '').lower()
        
        if not content:
            raise ValidationError('Note content is required')
            
        # Check for critical content
        for keyword, message in self.CRITICAL_CONTENT.items():
            if keyword in content:
                self.instance.needs_attention = True
                
        return content

    def validate_form_level_rules(self, cleaned_data):
        """Implement note-specific validation rules."""
        warnings = []
        critical_alerts = []
        
        content = cleaned_data.get('content', '').lower()
        category = cleaned_data.get('category')
        
        # Check for critical content
        for keyword, message in self.CRITICAL_CONTENT.items():
            if keyword in content:
                critical_alerts.append(f"CRITICAL NOTE: {message}")
        
        # Validate content length based on category
        if category in ['CLINICAL', 'VISITS'] and len(content.split()) < 20:
            warnings.append(
                f'Please provide more detailed content for {category} notes'
            )
        
        # Validate title descriptiveness
        title = cleaned_data.get('title', '')
        if len(title.split()) < 2:
            warnings.append(
                'Please provide a more descriptive title'
            )
        
        # Raise validation messages
        errors = []
        if critical_alerts:
            errors.extend(['CRITICAL NOTE ALERTS:', *critical_alerts])
        if warnings:
            errors.extend(['Validation Warnings:', *warnings])
        
        if errors:
            raise ValidationError({
                'non_field_errors': errors
            })

    def get_sections(self):
        """Define form sections for organized display."""
        return [
            {
                'title': 'Note Information',
                'description': 'Enter basic note details',
                'fields': ['title', 'date', 'category']
            },
            {
                'title': 'Note Content',
                'description': 'Enter detailed note content - critical information will be flagged',
                'fields': ['content']
            },
            {
                'title': 'Organization',
                'description': 'Organize and categorize the note',
                'fields': ['tags', 'is_pinned', 'source']
            }
        ]

    def save(self, commit=True):
        """Save form with additional processing for critical notes."""
        instance = super().save(commit=False)
        
        # Set needs_attention flag for critical content
        content = self.cleaned_data.get('content', '').lower()
        instance.needs_attention = (
            any(keyword in content for keyword in self.CRITICAL_CONTENT) or
            instance.needs_attention  # Preserve any existing flags
        )
        
        if commit:
            instance.save()
            self.save_m2m()  # Save many-to-many relationships
            
        return instance


class NoteAttachmentForm(SectionedMedicalForm):
    """Form for note attachments with enhanced validation and security."""
    
    # Allowed file types and their maximum sizes (in bytes)
    ALLOWED_FILE_TYPES = {
        'pdf': {
            'mime_type': 'application/pdf',
            'max_size': 10 * 1024 * 1024  # 10MB
        },
        'jpg': {
            'mime_type': 'image/jpeg',
            'max_size': 5 * 1024 * 1024  # 5MB
        },
        'png': {
            'mime_type': 'image/png',
            'max_size': 5 * 1024 * 1024  # 5MB
        },
        'doc': {
            'mime_type': 'application/msword',
            'max_size': 10 * 1024 * 1024  # 10MB
        },
        'docx': {
            'mime_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'max_size': 10 * 1024 * 1024  # 10MB
        }
    }
    
    class Meta:
        model = NoteAttachment
        fields = [
            'note',
            'file',
            'filename',
            'file_type'
        ]
        widgets = {
            'note': forms.Select(attrs={
                'class': 'form-control'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'filename': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'file_type': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': True
            })
        }
        help_texts = {
            'note': 'Note to attach this file to',
            'file': 'Select file to upload (PDF, JPG, PNG, DOC, DOCX only)',
            'filename': 'Original filename (set automatically)',
            'file_type': 'Type of file (set automatically)'
        }

    def clean_file(self):
        """Validate uploaded file."""
        file = self.cleaned_data.get('file')
        if not file:
            raise ValidationError('File is required')
            
        # Get file extension
        filename = file.name.lower()
        ext = filename.split('.')[-1] if '.' in filename else None
        
        # Validate file type
        if ext not in self.ALLOWED_FILE_TYPES:
            raise ValidationError(
                f'Invalid file type. Allowed types: {", ".join(self.ALLOWED_FILE_TYPES.keys())}'
            )
        
        # Validate file size
        if file.size > self.ALLOWED_FILE_TYPES[ext]['max_size']:
            max_mb = self.ALLOWED_FILE_TYPES[ext]['max_size'] / (1024 * 1024)
            raise ValidationError(
                f'File too large. Maximum size for {ext} files is {max_mb}MB'
            )
        
        return file

    def clean(self):
        """Set filename and file_type automatically."""
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        
        if file:
            # Set filename
            cleaned_data['filename'] = file.name
            
            # Set file type
            ext = file.name.lower().split('.')[-1] if '.' in file.name else None
            if ext in self.ALLOWED_FILE_TYPES:
                cleaned_data['file_type'] = self.ALLOWED_FILE_TYPES[ext]['mime_type']
        
        return cleaned_data

    def get_sections(self):
        """Define form sections for organized display."""
        return [
            {
                'title': 'File Upload',
                'description': 'Select file to attach to the note',
                'fields': ['note', 'file']
            },
            {
                'title': 'File Information',
                'description': 'File details (set automatically)',
                'fields': ['filename', 'file_type']
            }
        ] 