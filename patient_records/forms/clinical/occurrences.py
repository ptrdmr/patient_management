"""Occurrences form module."""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from ...models import Occurrences
from ..base import SectionedMedicalForm
from ...models.audit.constants import CLINICAL_AGGREGATE

class OccurrencesForm(SectionedMedicalForm):
    """Form for patient occurrences with enhanced validation and safety features."""
    
    aggregate_type = CLINICAL_AGGREGATE

    # Critical occurrence types requiring immediate attention
    CRITICAL_OCCURRENCES = {
        'fall': {
            'required_fields': ['action_taken'],
            'validation': 'Requires immediate assessment and documentation of injuries'
        },
        'medication_error': {
            'required_fields': ['action_taken', 'description'],
            'validation': 'Requires detailed documentation and immediate notification'
        },
        'adverse_reaction': {
            'required_fields': ['action_taken', 'description'],
            'validation': 'Requires immediate medical evaluation'
        },
        'security_incident': {
            'required_fields': ['action_taken', 'description'],
            'validation': 'Requires immediate security notification'
        },
        'equipment_failure': {
            'required_fields': ['action_taken', 'description'],
            'validation': 'Requires immediate equipment assessment'
        }
    }
    
    class Meta:
        model = Occurrences
        fields = [
            'date',
            'occurrence_type',
            'description',
            'action_taken',
            'notes',
            'source'
        ]
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'max': timezone.now().date().isoformat(),
                'class': 'form-control'
            }),
            'occurrence_type': forms.Select(attrs={
                'class': 'form-control',
                'autofocus': True
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Provide a detailed description of what occurred'
            }),
            'action_taken': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Document all actions taken in response to this occurrence'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Any additional relevant information'
            }),
            'source': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off'
            })
        }
        help_texts = {
            'date': 'Date when the occurrence happened',
            'occurrence_type': 'Select the type of occurrence - certain types require immediate action',
            'description': 'Provide a detailed description including who was involved and what happened',
            'action_taken': 'Document all actions taken, including notifications made and immediate responses',
            'notes': 'Additional notes about the occurrence, including follow-up plans',
            'source': 'Source of occurrence information (e.g., direct observation, reported by staff)'
        }

    def clean_occurrence_type(self):
        """Validate occurrence type and set needs_attention flag for critical occurrences."""
        occurrence_type = self.cleaned_data.get('occurrence_type', '').lower()
        
        if occurrence_type in self.CRITICAL_OCCURRENCES:
            self.instance.needs_attention = True
            
        return occurrence_type

    def validate_form_level_rules(self, cleaned_data):
        """Implement occurrence-specific validation rules."""
        warnings = []
        critical_alerts = []
        
        occurrence_type = cleaned_data.get('occurrence_type', '').lower()
        description = cleaned_data.get('description', '')
        action_taken = cleaned_data.get('action_taken', '')
        
        # Check critical occurrences
        if occurrence_type in self.CRITICAL_OCCURRENCES:
            occurrence_info = self.CRITICAL_OCCURRENCES[occurrence_type]
            critical_alerts.append(
                f"CRITICAL OCCURRENCE: {occurrence_type} - {occurrence_info['validation']}"
            )
            
            # Validate required fields based on occurrence type
            for field in occurrence_info['required_fields']:
                if not cleaned_data.get(field):
                    raise ValidationError({
                        field: f'This field is required for {occurrence_type} occurrences'
                    })
        
        # Validate description completeness
        if description:
            if len(description.split()) < 5:
                warnings.append(
                    'Description seems too brief. Please provide more detail.'
                )
        
        # Validate action taken for critical occurrences
        if occurrence_type in self.CRITICAL_OCCURRENCES and action_taken:
            if len(action_taken.split()) < 5:
                warnings.append(
                    'Action taken seems too brief for a critical occurrence.'
                )
        
        # Validate date is not in future
        date = cleaned_data.get('date')
        if date and date > timezone.now().date():
            raise ValidationError({
                'date': 'Occurrence date cannot be in the future'
            })
        
        # Raise validation messages
        errors = []
        if critical_alerts:
            errors.extend(['CRITICAL OCCURRENCE ALERTS:', *critical_alerts])
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
                'title': 'Occurrence Information',
                'description': 'Enter occurrence details - certain types require immediate action',
                'fields': ['date', 'occurrence_type']
            },
            {
                'title': 'Description and Response',
                'description': 'Provide detailed information about what happened and actions taken',
                'fields': ['description', 'action_taken']
            },
            {
                'title': 'Additional Information',
                'description': 'Enter any additional details and documentation',
                'fields': ['notes', 'source']
            }
        ]

    def save(self, commit=True):
        """Save form with additional processing for critical occurrences."""
        instance = super().save(commit=False)
        
        # Set needs_attention flag for critical occurrences
        occurrence_type = self.cleaned_data.get('occurrence_type', '').lower()
        instance.needs_attention = (
            occurrence_type in self.CRITICAL_OCCURRENCES or
            instance.needs_attention  # Preserve any existing flags
        )
        
        if commit:
            instance.save()
            
        return instance 