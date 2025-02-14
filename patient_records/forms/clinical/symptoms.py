"""Symptoms form module."""

from django import forms
from django.core.exceptions import ValidationError
from ...models import Symptoms
from ..base import SectionedMedicalForm
from ...models.audit.constants import CLINICAL_AGGREGATE

class SymptomsForm(SectionedMedicalForm):
    """Form for patient symptoms with enhanced validation and security."""
    
    aggregate_type = CLINICAL_AGGREGATE

    # Common symptoms that require immediate attention
    CRITICAL_SYMPTOMS = {
        'chest pain',
        'shortness of breath',
        'difficulty breathing',
        'severe headache',
        'sudden confusion',
        'sudden weakness',
        'severe abdominal pain',
        'coughing blood',
        'suicidal thoughts',
        'seizure'
    }
    
    class Meta:
        model = Symptoms
        fields = [
            'date',
            'symptom',
            'severity',
            'notes',
            'person_reporting',
            'provider',
            'source'
        ]
        widgets = {
            'symptom': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off',  # Prevent browser autocomplete for medical data
                'placeholder': 'Enter primary symptom'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Enter additional details about the symptom'
            }),
            'severity': forms.Select(
                choices=Symptoms.SEVERITY_CHOICES,
                attrs={'class': 'form-control'}
            ),
            'person_reporting': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name and relationship to patient'
            })
        }
        help_texts = {
            'date': 'Date when symptom was reported',
            'symptom': 'Primary symptom description',
            'severity': 'Rate the severity of the symptom from 1 (minimal) to 5 (very severe)',
            'notes': 'Additional details, timing, frequency, or related symptoms',
            'person_reporting': 'Name and relationship of person reporting the symptom',
            'provider': 'Healthcare provider who assessed this symptom',
            'source': 'How this information was collected'
        }

    def clean_symptom(self):
        """Clean and validate the symptom field."""
        symptom = self.cleaned_data.get('symptom', '').lower().strip()
        
        if not symptom:
            raise ValidationError('Symptom description is required')
            
        # Check for critical symptoms
        if any(critical in symptom for critical in self.CRITICAL_SYMPTOMS):
            self.instance.needs_attention = True
            
        return symptom.capitalize()

    def validate_form_level_rules(self, cleaned_data):
        """Implement symptom-specific validation rules."""
        warnings = []
        critical_alerts = []
        
        # Get the main fields
        symptom = cleaned_data.get('symptom', '').lower()
        severity = cleaned_data.get('severity')
        notes = cleaned_data.get('notes', '')
        
        # Check for critical symptoms
        if any(critical in symptom for critical in self.CRITICAL_SYMPTOMS):
            critical_alerts.append(
                f"ATTENTION: '{cleaned_data.get('symptom')}' may require immediate medical attention"
            )
        
        # Validate severity matches description
        if severity in [4, 5] and 'mild' in (symptom + ' ' + notes).lower():
            warnings.append(
                "High severity rating (4-5) seems inconsistent with description containing 'mild'"
            )
        if severity in [1, 2] and any(word in (symptom + ' ' + notes).lower() 
                                    for word in ['severe', 'extreme', 'intense']):
            warnings.append(
                "Low severity rating (1-2) seems inconsistent with description containing "
                "'severe', 'extreme', or 'intense'"
            )
        
        # Validate notes provide sufficient detail for severe symptoms
        if severity in [4, 5] and len(notes.strip()) < 20:
            warnings.append(
                "Please provide more detailed notes for high severity symptoms"
            )
        
        # Raise validation messages
        errors = []
        if critical_alerts:
            errors.extend(['CRITICAL SYMPTOMS REPORTED:', *critical_alerts])
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
                'title': 'Symptom Information',
                'description': 'Enter primary symptom details',
                'fields': ['date', 'symptom', 'severity']
            },
            {
                'title': 'Additional Information',
                'description': 'Enter additional details and context',
                'fields': ['notes', 'person_reporting', 'provider']
            },
            {
                'title': 'Source',
                'description': 'Enter information source',
                'fields': ['source']
            }
        ]

    def save(self, commit=True):
        """Save form with additional processing for critical symptoms."""
        instance = super().save(commit=False)
        
        # Set needs_attention flag for critical symptoms
        symptom = self.cleaned_data.get('symptom', '').lower()
        severity = self.cleaned_data.get('severity')
        
        instance.needs_attention = (
            any(critical in symptom for critical in self.CRITICAL_SYMPTOMS) or 
            severity in [4, 5]
        )
        
        if commit:
            instance.save()
            
        return instance 