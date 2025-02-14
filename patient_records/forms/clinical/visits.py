"""Visits form module."""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from ...models import Visits
from ..base import SectionedMedicalForm
from ...models.audit.constants import CLINICAL_AGGREGATE

class VisitsForm(SectionedMedicalForm):
    """Form for patient visits with enhanced validation and safety features."""
    
    aggregate_type = CLINICAL_AGGREGATE

    # Critical complaints requiring immediate attention
    CRITICAL_COMPLAINTS = {
        'chest pain': 'Possible cardiac event - requires immediate evaluation',
        'shortness of breath': 'Respiratory distress - requires immediate assessment',
        'severe pain': 'Severe pain - requires immediate pain management',
        'fall': 'Fall incident - requires immediate injury assessment',
        'mental status change': 'Mental status change - requires neurological evaluation',
        'fever': 'Fever in vulnerable patient - requires immediate assessment',
        'bleeding': 'Active bleeding - requires immediate evaluation'
    }

    # Visit types and their requirements
    VISIT_REQUIREMENTS = {
        'EMERGENCY': {
            'required_fields': ['chief_complaint', 'notes', 'provider'],
            'max_followup_days': 7,
            'needs_attention': True
        },
        'HOSPITAL': {
            'required_fields': ['chief_complaint', 'notes', 'provider'],
            'max_followup_days': 14,
            'needs_attention': True
        },
        'HOME': {
            'required_fields': ['chief_complaint', 'provider'],
            'max_followup_days': 30,
            'needs_attention': False
        },
        'OFFICE': {
            'required_fields': ['chief_complaint', 'provider'],
            'max_followup_days': 90,
            'needs_attention': False
        },
        'VIRTUAL': {
            'required_fields': ['chief_complaint', 'provider'],
            'max_followup_days': 30,
            'needs_attention': False
        }
    }
    
    class Meta:
        model = Visits
        fields = [
            'provider',
            'date',
            'visit_type',
            'practice',
            'chief_complaint',
            'notes',
            'follow_up_needed',
            'follow_up_date',
            'source'
        ]
        widgets = {
            'provider': forms.Select(attrs={
                'class': 'form-control'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'max': timezone.now().date().isoformat(),
                'class': 'form-control'
            }),
            'visit_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'practice': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off'
            }),
            'chief_complaint': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Enter primary reason for visit'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Enter detailed visit notes, findings, and plan'
            }),
            'follow_up_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'source': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off'
            })
        }
        help_texts = {
            'provider': 'Healthcare provider conducting the visit',
            'date': 'Date when visit occurred',
            'visit_type': 'Type of visit - certain types require specific documentation',
            'practice': 'Medical practice or facility where visit occurred',
            'chief_complaint': 'Primary reason for visit - critical complaints will be flagged',
            'notes': 'Detailed visit notes including assessment, plan, and any critical findings',
            'follow_up_needed': 'Indicate if follow-up care is needed',
            'follow_up_date': 'When follow-up should occur - will be validated based on visit type',
            'source': 'Source of visit information (e.g., direct care, transferred records)'
        }

    def clean(self):
        """Validate form data and relationships between fields."""
        cleaned_data = super().clean()
        
        # Validate date is not in future
        date = cleaned_data.get('date')
        if date and date > timezone.now().date():
            raise ValidationError({
                'date': 'Visit date cannot be in the future'
            })
        
        # Validate follow-up date logic
        follow_up_needed = cleaned_data.get('follow_up_needed')
        follow_up_date = cleaned_data.get('follow_up_date')
        visit_type = cleaned_data.get('visit_type')
        
        if follow_up_needed and not follow_up_date:
            raise ValidationError({
                'follow_up_date': 'Follow-up date is required when follow-up is needed'
            })
        
        if follow_up_date:
            if follow_up_date <= date:
                raise ValidationError({
                    'follow_up_date': 'Follow-up date must be after visit date'
                })
            
            if visit_type in self.VISIT_REQUIREMENTS:
                max_days = self.VISIT_REQUIREMENTS[visit_type]['max_followup_days']
                if follow_up_date > date + timedelta(days=max_days):
                    raise ValidationError({
                        'follow_up_date': f'Follow-up for {visit_type} visits should be within {max_days} days'
                    })
        
        return cleaned_data

    def validate_form_level_rules(self, cleaned_data):
        """Implement visit-specific validation rules."""
        warnings = []
        critical_alerts = []
        
        visit_type = cleaned_data.get('visit_type')
        chief_complaint = cleaned_data.get('chief_complaint', '').lower()
        notes = cleaned_data.get('notes', '')
        
        # Check visit type requirements
        if visit_type in self.VISIT_REQUIREMENTS:
            requirements = self.VISIT_REQUIREMENTS[visit_type]
            
            # Set needs_attention based on visit type
            if requirements['needs_attention']:
                self.instance.needs_attention = True
                critical_alerts.append(f"ATTENTION: {visit_type} visit requires immediate review")
            
            # Validate required fields
            for field in requirements['required_fields']:
                if not cleaned_data.get(field):
                    raise ValidationError({
                        field: f'This field is required for {visit_type} visits'
                    })
        
        # Check for critical complaints
        for keyword, message in self.CRITICAL_COMPLAINTS.items():
            if keyword in chief_complaint:
                critical_alerts.append(f"CRITICAL COMPLAINT: {message}")
                self.instance.needs_attention = True
        
        # Validate notes completeness
        if visit_type in ['EMERGENCY', 'HOSPITAL'] and notes:
            if len(notes.split()) < 20:
                warnings.append(
                    f'Please provide more detailed notes for {visit_type} visits'
                )
        
        # Validate chief complaint completeness
        if chief_complaint:
            if len(chief_complaint.split()) < 3:
                warnings.append(
                    'Please provide a more detailed chief complaint'
                )
        
        # Raise validation messages
        errors = []
        if critical_alerts:
            errors.extend(['CRITICAL VISIT ALERTS:', *critical_alerts])
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
                'title': 'Visit Information',
                'description': 'Enter basic visit details',
                'fields': ['date', 'visit_type', 'provider', 'practice']
            },
            {
                'title': 'Clinical Information',
                'description': 'Document clinical details - critical complaints will be flagged',
                'fields': ['chief_complaint', 'notes']
            },
            {
                'title': 'Follow-up Planning',
                'description': 'Document follow-up requirements',
                'fields': ['follow_up_needed', 'follow_up_date']
            },
            {
                'title': 'Additional Information',
                'description': 'Enter any additional documentation',
                'fields': ['source']
            }
        ]

    def save(self, commit=True):
        """Save form with additional processing for critical visits."""
        instance = super().save(commit=False)
        
        # Set needs_attention flag for critical complaints or visit types
        chief_complaint = self.cleaned_data.get('chief_complaint', '').lower()
        visit_type = self.cleaned_data.get('visit_type')
        
        instance.needs_attention = (
            any(keyword in chief_complaint for keyword in self.CRITICAL_COMPLAINTS) or
            (visit_type in self.VISIT_REQUIREMENTS and 
             self.VISIT_REQUIREMENTS[visit_type]['needs_attention']) or
            instance.needs_attention  # Preserve any existing flags
        )
        
        if commit:
            instance.save()
            
        return instance