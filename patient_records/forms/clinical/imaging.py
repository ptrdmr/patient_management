"""Imaging form module."""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from ...models import Imaging
from ..base import SectionedMedicalForm
from ...models.audit.constants import CLINICAL_AGGREGATE

class ImagingForm(SectionedMedicalForm):
    """Form for patient imaging studies with enhanced validation and safety features."""
    
    aggregate_type = CLINICAL_AGGREGATE

    # Critical findings requiring immediate attention
    CRITICAL_FINDINGS = {
        'hemorrhage': 'Intracranial hemorrhage - requires immediate neurology consult',
        'fracture': 'Acute fracture - requires orthopedic evaluation',
        'pneumothorax': 'Pneumothorax - requires immediate cardiopulmonary assessment',
        'mass': 'Suspicious mass - requires oncology referral',
        'embolism': 'Pulmonary embolism - requires immediate intervention',
        'aneurysm': 'Aneurysm - requires vascular surgery consult',
        'obstruction': 'Bowel obstruction - requires surgical evaluation'
    }

    # Imaging types and their requirements
    IMAGING_REQUIREMENTS = {
        'CT': {
            'required_fields': ['body_part', 'findings'],
            'contrast_warning': True
        },
        'MRI': {
            'required_fields': ['body_part', 'findings'],
            'contrast_warning': True
        },
        'X-Ray': {
            'required_fields': ['body_part', 'findings'],
            'contrast_warning': False
        },
        'Ultrasound': {
            'required_fields': ['body_part', 'findings'],
            'contrast_warning': False
        },
        'PET': {
            'required_fields': ['body_part', 'findings'],
            'contrast_warning': True
        }
    }
    
    class Meta:
        model = Imaging
        fields = [
            'date',
            'type',
            'body_part',
            'findings',
            'notes',
            'source'
        ]
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'max': timezone.now().date().isoformat(),
                'class': 'form-control'
            }),
            'type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'body_part': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Specify the anatomical region'
            }),
            'findings': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Enter detailed imaging findings and interpretation'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Enter additional notes, recommendations, or follow-up plans'
            }),
            'source': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off'
            })
        }
        help_texts = {
            'date': 'Date when imaging was performed',
            'type': 'Type of imaging study - certain types have specific requirements',
            'body_part': 'Specific anatomical region or body part examined',
            'findings': 'Detailed findings, interpretation, and any critical results',
            'notes': 'Additional notes, recommendations, and follow-up plans',
            'source': 'Source of imaging (e.g., facility name, PACS system)'
        }

    def clean(self):
        """Validate form data and relationships between fields."""
        cleaned_data = super().clean()
        
        # Validate date is not in future
        date = cleaned_data.get('date')
        if date and date > timezone.now().date():
            raise ValidationError({
                'date': 'Imaging date cannot be in the future'
            })
        
        # Validate required fields based on imaging type
        imaging_type = cleaned_data.get('type')
        if imaging_type and imaging_type in self.IMAGING_REQUIREMENTS:
            requirements = self.IMAGING_REQUIREMENTS[imaging_type]
            for field in requirements['required_fields']:
                if not cleaned_data.get(field):
                    raise ValidationError({
                        field: f'This field is required for {imaging_type} studies'
                    })
        
        return cleaned_data

    def validate_form_level_rules(self, cleaned_data):
        """Implement imaging-specific validation rules."""
        warnings = []
        critical_alerts = []
        
        findings = cleaned_data.get('findings', '').lower()
        imaging_type = cleaned_data.get('type')
        
        # Check for critical findings
        for keyword, message in self.CRITICAL_FINDINGS.items():
            if keyword in findings:
                critical_alerts.append(f"CRITICAL FINDING: {message}")
                self.instance.needs_attention = True
        
        # Add contrast warnings if applicable
        if imaging_type in self.IMAGING_REQUIREMENTS:
            if self.IMAGING_REQUIREMENTS[imaging_type]['contrast_warning']:
                warnings.append(
                    f"ATTENTION: {imaging_type} may require contrast - verify allergies and renal function"
                )
        
        # Validate findings completeness
        if findings:
            if len(findings.split()) < 10:
                warnings.append(
                    'Please provide more detailed imaging findings'
                )
        
        # Raise validation messages
        errors = []
        if critical_alerts:
            errors.extend(['CRITICAL IMAGING ALERTS:', *critical_alerts])
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
                'title': 'Study Information',
                'description': 'Enter imaging study details',
                'fields': ['date', 'type', 'body_part']
            },
            {
                'title': 'Results',
                'description': 'Document findings and interpretation - critical results will be flagged',
                'fields': ['findings']
            },
            {
                'title': 'Additional Information',
                'description': 'Enter additional notes and documentation',
                'fields': ['notes', 'source']
            }
        ]

    def save(self, commit=True):
        """Save form with additional processing for critical findings."""
        instance = super().save(commit=False)
        
        # Set needs_attention flag for critical findings
        findings = self.cleaned_data.get('findings', '').lower()
        instance.needs_attention = (
            any(keyword in findings for keyword in self.CRITICAL_FINDINGS) or
            instance.needs_attention  # Preserve any existing flags
        )
        
        if commit:
            instance.save()
            
        return instance 