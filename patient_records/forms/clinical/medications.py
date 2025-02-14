"""Medications form module."""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from ...models import Medications
from ..base import SectionedMedicalForm
from ...models.audit.constants import CLINICAL_AGGREGATE
import re

class MedicationsForm(SectionedMedicalForm):
    """Form for patient medications with enhanced validation and safety features."""
    
    aggregate_type = CLINICAL_AGGREGATE

    # High-alert medications requiring extra validation
    HIGH_ALERT_MEDICATIONS = {
        'warfarin': {
            'max_daily_dose': '10mg',
            'monitoring': 'Requires regular INR monitoring'
        },
        'insulin': {
            'monitoring': 'Requires blood glucose monitoring'
        },
        'digoxin': {
            'max_daily_dose': '250mcg',
            'monitoring': 'Requires regular potassium and creatinine monitoring'
        },
        'methotrexate': {
            'max_weekly_dose': '25mg',
            'monitoring': 'Requires regular CBC and liver function monitoring'
        },
        'morphine': {
            'monitoring': 'Requires regular respiratory monitoring'
        },
        'fentanyl': {
            'monitoring': 'Requires regular respiratory monitoring'
        }
    }

    # Common drug units for validation
    COMMON_UNITS = {
        'mg': r'^\d+(\.\d+)?mg$',
        'mcg': r'^\d+(\.\d+)?mcg$',
        'g': r'^\d+(\.\d+)?g$',
        'ml': r'^\d+(\.\d+)?ml$',
        'units': r'^\d+(\.\d+)?units$'
    }
    
    class Meta:
        model = Medications
        fields = [
            'date_prescribed',
            'drug',
            'dose',
            'route',
            'frequency',
            'prn',
            'dc_date',
            'provider',
            'notes',
            'source'
        ]
        widgets = {
            'drug': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off',  # Prevent browser autocomplete for medications
                'placeholder': 'Enter medication name'
            }),
            'dose': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 10mg, 500mcg'
            }),
            'frequency': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Once daily, Every 4 hours'
            }),
            'route': forms.Select(
                choices=Medications.ROUTE_CHOICES,
                attrs={'class': 'form-control'}
            ),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Enter additional notes, warnings, or instructions'
            }),
            'dc_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control date-input',
                'value': '',  # Ensure empty by default
                'data-empty': 'true',  # Custom attribute to track empty state
                'placeholder': 'Leave blank if medication is active'
            })
        }
        help_texts = {
            'date_prescribed': 'Date when medication was prescribed',
            'drug': 'Full medication name (generic or brand name)',
            'dose': 'Medication dose with units (e.g., 10mg, 500mcg)',
            'route': 'How the medication should be administered',
            'frequency': 'How often to take the medication',
            'prn': 'Check if this is an as-needed medication',
            'dc_date': 'Leave blank if medication is currently active. Only fill this in when discontinuing the medication.',
            'provider': 'Healthcare provider who prescribed this medication',
            'notes': 'Additional instructions, warnings, or monitoring requirements',
            'source': 'Source of medication information'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make dc_date field not required and ensure it starts empty
        self.fields['dc_date'].required = False
        self.fields['dc_date'].initial = None
        
        # Set max date for date_prescribed to today
        self.fields['date_prescribed'].widget.attrs['max'] = timezone.now().date().isoformat()
        self.fields['date_prescribed'].initial = timezone.now().date()
        
        # Ensure dc_date field is truly empty on form load
        if not self.instance.pk:  # Only for new instances
            self.fields['dc_date'].widget.attrs['value'] = ''

    def clean_drug(self):
        """Clean and validate the drug name."""
        drug = self.cleaned_data.get('drug', '').lower().strip()
        
        if not drug:
            raise ValidationError('Medication name is required')
            
        return drug.title()

    def clean_dose(self):
        """Clean and validate the dose."""
        dose = self.cleaned_data.get('dose', '').lower().strip()
        
        if not dose:
            raise ValidationError('Dose is required')
            
        # Validate dose format
        valid_format = any(
            re.match(pattern, dose)
            for pattern in self.COMMON_UNITS.values()
        )
        
        if not valid_format:
            raise ValidationError(
                'Invalid dose format. Please include units (e.g., 10mg, 500mcg)'
            )
            
        return dose

    def clean_dc_date(self):
        """Clean dc_date field to ensure empty values are handled correctly."""
        dc_date = self.cleaned_data.get('dc_date')
        if dc_date and isinstance(dc_date, str) and not dc_date.strip():
            return None
        return dc_date

    def validate_form_level_rules(self, cleaned_data):
        """Implement medication-specific validation rules."""
        warnings = []
        critical_alerts = []
        
        drug = cleaned_data.get('drug', '').lower()
        dose = cleaned_data.get('dose', '').lower()
        frequency = cleaned_data.get('frequency', '').lower()
        
        # Check high-alert medications
        if drug in self.HIGH_ALERT_MEDICATIONS:
            med_info = self.HIGH_ALERT_MEDICATIONS[drug]
            critical_alerts.append(
                f"HIGH-ALERT MEDICATION: {drug.title()} - {med_info['monitoring']}"
            )
            
            # Check maximum doses if specified
            if 'max_daily_dose' in med_info:
                warnings.append(
                    f"Verify dose against maximum daily dose: {med_info['max_daily_dose']}"
                )
            if 'max_weekly_dose' in med_info:
                warnings.append(
                    f"Verify dose against maximum weekly dose: {med_info['max_weekly_dose']}"
                )
        
        # Validate frequency format
        if frequency:
            if 'prn' in frequency.lower() and not cleaned_data.get('prn'):
                warnings.append(
                    "Frequency contains 'PRN' but PRN checkbox is not selected"
                )
        
        # Validate date logic
        date_prescribed = cleaned_data.get('date_prescribed')
        dc_date = cleaned_data.get('dc_date')
        
        if date_prescribed and dc_date:
            if dc_date < date_prescribed:
                raise ValidationError({
                    'dc_date': 'Discontinue date cannot be earlier than prescribed date'
                })
            
            if (dc_date - date_prescribed).days > 365:
                warnings.append(
                    'Medication duration exceeds 1 year - please verify long-term use'
                )
        
        # Raise validation messages
        errors = []
        if critical_alerts:
            errors.extend(['CRITICAL MEDICATION ALERTS:', *critical_alerts])
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
                'title': 'Medication Information',
                'description': 'Enter primary medication details',
                'fields': ['drug', 'dose', 'route', 'frequency']
            },
            {
                'title': 'Prescription Dates',
                'description': 'Enter when medication was prescribed and discontinued',
                'fields': ['date_prescribed', 'dc_date']
            },
            {
                'title': 'Additional Information',
                'description': 'Enter additional details and instructions',
                'fields': ['prn', 'provider', 'notes', 'source']
            }
        ]

    def save(self, commit=True):
        """Save form with additional processing."""
        instance = super(SectionedMedicalForm, self).save(commit=False)
        
        # Set date to match date_prescribed
        instance.date = instance.date_prescribed
        
        if commit:
            instance.save()
            
        return instance 