"""ADLs form module."""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from ...models import Adls
from ..base import SectionedMedicalForm
from ...models.audit.constants import CLINICAL_AGGREGATE

class AdlsForm(SectionedMedicalForm):
    """Form for activities of daily living with enhanced validation and safety features."""
    
    aggregate_type = CLINICAL_AGGREGATE

    # ADL status levels requiring attention
    CRITICAL_STATUS = {
        'Dependent': {
            'validation': 'Complete dependence - requires full assistance',
            'required_fields': ['notes']
        },
        'Maximum Assist': {
            'validation': 'Requires maximum assistance - safety concerns',
            'required_fields': ['notes']
        }
    }

    # ADL domains and their significance
    ADL_DOMAINS = {
        'ambulation': {
            'description': 'Ability to walk/move around safely',
            'risk_levels': ['Dependent', 'Maximum Assist']
        },
        'transfer': {
            'description': 'Ability to move between positions safely',
            'risk_levels': ['Dependent', 'Maximum Assist']
        },
        'toileting': {
            'description': 'Ability to use the toilet safely',
            'risk_levels': ['Dependent', 'Maximum Assist']
        },
        'feeding': {
            'description': 'Ability to eat and drink safely',
            'risk_levels': ['Dependent', 'Maximum Assist']
        },
        'bathing': {
            'description': 'Ability to maintain hygiene safely',
            'risk_levels': ['Dependent', 'Maximum Assist']
        }
    }
    
    class Meta:
        model = Adls
        fields = [
            'date',
            'ambulation',
            'continence',
            'transfer',
            'toileting',
            'transferring',
            'dressing',
            'feeding',
            'bathing',
            'notes',
            'source'
        ]
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'max': timezone.now().date().isoformat(),
                'class': 'form-control'
            }),
            'ambulation': forms.Select(attrs={
                'class': 'form-control'
            }),
            'continence': forms.Select(attrs={
                'class': 'form-control'
            }),
            'transfer': forms.Select(attrs={
                'class': 'form-control'
            }),
            'toileting': forms.Select(attrs={
                'class': 'form-control'
            }),
            'transferring': forms.Select(attrs={
                'class': 'form-control'
            }),
            'dressing': forms.Select(attrs={
                'class': 'form-control'
            }),
            'feeding': forms.Select(attrs={
                'class': 'form-control'
            }),
            'bathing': forms.Select(attrs={
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Enter detailed notes about ADL status and assistance needs'
            }),
            'source': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off'
            })
        }
        help_texts = {
            'date': 'Date of ADL assessment',
            'ambulation': 'Assess ability to walk/move around safely - note any assistance needed',
            'continence': 'Assess bladder/bowel control and management',
            'transfer': 'Assess ability to move between positions safely',
            'toileting': 'Assess ability to use the toilet safely and maintain hygiene',
            'transferring': 'Assess ability to transfer between surfaces safely',
            'dressing': 'Assess ability to select and put on clothing appropriately',
            'feeding': 'Assess ability to eat and drink safely and independently',
            'bathing': 'Assess ability to wash and maintain personal hygiene',
            'notes': 'Document specific assistance needs, safety concerns, and recommendations',
            'source': 'Source of ADL assessment (e.g., direct observation, therapy evaluation)'
        }

    def clean(self):
        """Validate form data and check for significant changes."""
        cleaned_data = super().clean()
        
        # Check for date in future
        date = cleaned_data.get('date')
        if date and date > timezone.now().date():
            raise ValidationError({
                'date': 'Assessment date cannot be in the future'
            })
        
        return cleaned_data

    def validate_form_level_rules(self, cleaned_data):
        """Implement ADL-specific validation rules."""
        warnings = []
        critical_alerts = []
        
        # Check each ADL domain for critical status
        for domain, info in self.ADL_DOMAINS.items():
            status = cleaned_data.get(domain)
            if status in self.CRITICAL_STATUS:
                critical_alerts.append(
                    f"ATTENTION: {domain.title()} - {self.CRITICAL_STATUS[status]['validation']}"
                )
                self.instance.needs_attention = True
                
                # Validate required fields for critical status
                for field in self.CRITICAL_STATUS[status]['required_fields']:
                    if not cleaned_data.get(field):
                        raise ValidationError({
                            field: f'This field is required when {domain} is {status}'
                        })
        
        # Check for significant changes if this isn't the first assessment
        if self.instance.patient:
            previous = Adls.objects.filter(
                patient=self.instance.patient,
                date__lt=cleaned_data.get('date')
            ).order_by('-date').first()
            
            if previous:
                for domain in self.ADL_DOMAINS:
                    current = cleaned_data.get(domain)
                    prev_value = getattr(previous, domain)
                    if current and prev_value and current != prev_value:
                        if current in self.CRITICAL_STATUS:
                            warnings.append(
                                f"Decline in {domain} status from {prev_value} to {current}"
                            )
        
        # Validate notes completeness for critical statuses
        notes = cleaned_data.get('notes', '')
        if any(cleaned_data.get(domain) in self.CRITICAL_STATUS 
               for domain in self.ADL_DOMAINS):
            if len(notes.split()) < 10:
                warnings.append(
                    'Please provide more detailed notes for critical ADL statuses'
                )
        
        # Raise validation messages
        errors = []
        if critical_alerts:
            errors.extend(['CRITICAL ADL ALERTS:', *critical_alerts])
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
                'title': 'Assessment Information',
                'description': 'Enter assessment date and source',
                'fields': ['date', 'source']
            },
            {
                'title': 'Mobility and Transfers',
                'description': 'Assess mobility and transfer capabilities',
                'fields': ['ambulation', 'transfer', 'transferring']
            },
            {
                'title': 'Self-Care Activities',
                'description': 'Assess ability to perform self-care tasks',
                'fields': ['toileting', 'dressing', 'feeding', 'bathing']
            },
            {
                'title': 'Additional Assessment',
                'description': 'Document continence and additional notes',
                'fields': ['continence', 'notes']
            }
        ]

    def save(self, commit=True):
        """Save form with additional processing for critical ADL statuses."""
        instance = super().save(commit=False)
        
        # Set needs_attention flag for critical ADL statuses
        instance.needs_attention = any(
            getattr(instance, domain) in self.CRITICAL_STATUS
            for domain in self.ADL_DOMAINS
        )
        
        if commit:
            instance.save()
            
        return instance 