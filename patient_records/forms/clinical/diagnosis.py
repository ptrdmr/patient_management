"""Diagnosis form module."""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from ...models import Diagnosis
from ..base import SectionedMedicalForm
from ...models.audit.constants import CLINICAL_AGGREGATE
import re

class DiagnosisForm(SectionedMedicalForm):
    """Form for patient diagnoses with enhanced validation and safety features."""
    
    aggregate_type = CLINICAL_AGGREGATE

    # Critical diagnoses requiring immediate attention
    CRITICAL_DIAGNOSES = {
        'C': {  # Cancer diagnoses
            'validation': 'Cancer diagnosis - requires oncology referral and care plan',
            'required_fields': ['provider', 'notes']
        },
        'I21': {  # Acute MI
            'validation': 'Acute Myocardial Infarction - requires immediate cardiac evaluation',
            'required_fields': ['provider', 'notes']
        },
        'J96': {  # Respiratory failure
            'validation': 'Respiratory Failure - requires immediate respiratory assessment',
            'required_fields': ['provider', 'notes']
        },
        'R57': {  # Shock
            'validation': 'Shock - requires immediate medical intervention',
            'required_fields': ['provider', 'notes']
        },
        'K72': {  # Hepatic failure
            'validation': 'Hepatic Failure - requires immediate hepatology consultation',
            'required_fields': ['provider', 'notes']
        }
    }
    
    class Meta:
        model = Diagnosis
        fields = [
            'icd_code',
            'diagnosis',
            'date',
            'provider',
            'notes',
            'is_active',
            'resolved_date',
            'source'
        ]
        widgets = {
            'icd_code': forms.TextInput(attrs={
                'class': 'form-control',
                'pattern': r'^[A-Z]\d{2}(\.\d{1,2})?$',
                'placeholder': 'e.g., E11.9'
            }),
            'diagnosis': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'max': timezone.now().date().isoformat(),
                'class': 'form-control'
            }),
            'resolved_date': forms.DateInput(attrs={
                'type': 'date',
                'max': timezone.now().date().isoformat(),
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Enter detailed notes about the diagnosis'
            }),
            'provider': forms.Select(attrs={
                'class': 'form-control'
            }),
            'source': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off'
            })
        }
        help_texts = {
            'icd_code': 'ICD-10 code for the diagnosis (e.g., E11.9)',
            'diagnosis': 'Full description of the diagnosis',
            'date': 'Date when diagnosis was made or confirmed',
            'provider': 'Healthcare provider who made or confirmed the diagnosis',
            'notes': 'Detailed notes including symptoms, severity, and treatment plan',
            'is_active': 'Whether this diagnosis is currently active',
            'resolved_date': 'Date when the diagnosis was resolved (if applicable)',
            'source': 'Source of diagnosis information (e.g., direct evaluation, transferred records)'
        }

    def clean_icd_code(self):
        """Validate ICD code format and check for critical diagnoses."""
        icd_code = self.cleaned_data.get('icd_code', '').strip()
        
        if not icd_code:
            raise ValidationError('ICD code is required')
            
        # Validate ICD-10 format
        if not re.match(r'^[A-Z]\d{2}(\.\d{1,2})?$', icd_code):
            raise ValidationError(
                'Invalid ICD-10 format. Must be letter followed by 2 digits, '
                'optionally followed by decimal and 1-2 digits (e.g., E11.9)'
            )
            
        # Check for critical diagnoses
        code_prefix = icd_code.split('.')[0]
        if any(code_prefix.startswith(critical) for critical in self.CRITICAL_DIAGNOSES):
            self.instance.needs_attention = True
            
        return icd_code

    def clean(self):
        """Validate form data and relationships between fields."""
        cleaned_data = super().clean()
        
        date = cleaned_data.get('date')
        resolved_date = cleaned_data.get('resolved_date')
        is_active = cleaned_data.get('is_active')
        
        if date and resolved_date and resolved_date < date:
            raise ValidationError({
                'resolved_date': 'Resolution date cannot be earlier than diagnosis date'
            })
            
        if resolved_date and is_active:
            raise ValidationError({
                'is_active': 'Diagnosis cannot be both active and resolved'
            })
            
        if not is_active and not resolved_date:
            raise ValidationError({
                'resolved_date': 'Please provide a resolution date for inactive diagnoses'
            })
            
        return cleaned_data

    def validate_form_level_rules(self, cleaned_data):
        """Implement diagnosis-specific validation rules."""
        warnings = []
        critical_alerts = []
        
        icd_code = cleaned_data.get('icd_code', '').split('.')[0]
        diagnosis = cleaned_data.get('diagnosis', '')
        notes = cleaned_data.get('notes', '')
        
        # Check critical diagnoses
        for prefix, info in self.CRITICAL_DIAGNOSES.items():
            if icd_code.startswith(prefix):
                critical_alerts.append(
                    f"CRITICAL DIAGNOSIS: {info['validation']}"
                )
                
                # Validate required fields
                for field in info['required_fields']:
                    if not cleaned_data.get(field):
                        raise ValidationError({
                            field: f'This field is required for this critical diagnosis'
                        })
        
        # Validate notes completeness for critical diagnoses
        if any(icd_code.startswith(critical) for critical in self.CRITICAL_DIAGNOSES):
            if len(notes.split()) < 10:
                warnings.append(
                    'Please provide more detailed notes for this critical diagnosis'
                )
        
        # Validate diagnosis description
        if len(diagnosis.split()) < 2:
            warnings.append(
                'Please provide a more detailed diagnosis description'
            )
        
        # Raise validation messages
        errors = []
        if critical_alerts:
            errors.extend(['CRITICAL DIAGNOSIS ALERTS:', *critical_alerts])
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
                'title': 'Diagnosis Information',
                'description': 'Enter the primary diagnosis details - certain diagnoses require immediate attention',
                'fields': ['icd_code', 'diagnosis', 'date', 'provider']
            },
            {
                'title': 'Status and Documentation',
                'description': 'Document current status and provide detailed notes',
                'fields': ['is_active', 'resolved_date', 'notes']
            },
            {
                'title': 'Additional Information',
                'description': 'Enter any additional details and documentation',
                'fields': ['source']
            }
        ]

    def save(self, commit=True):
        """Save form with additional processing for critical diagnoses."""
        instance = super().save(commit=False)
        
        # Set needs_attention flag for critical diagnoses
        icd_code = self.cleaned_data.get('icd_code', '').split('.')[0]
        instance.needs_attention = (
            any(icd_code.startswith(critical) for critical in self.CRITICAL_DIAGNOSES) or
            instance.needs_attention  # Preserve any existing flags
        )
        
        if commit:
            instance.save()
            
        return instance 