"""Vitals form module."""

from django import forms
from ...models import Vitals
from ..base import SectionedMedicalForm
from ..mixins.validation import DateValidationMixin
from django.core.exceptions import ValidationError

class VitalsForm(SectionedMedicalForm):
    """Form for patient vital signs with enhanced validation and security."""
    
    class Meta:
        model = Vitals
        fields = [
            'date',
            'blood_pressure',
            'temperature',
            'spo2',
            'pulse',
            'respirations',
            'supp_o2',
            'pain',
            'source'
        ]
        widgets = {
            'blood_pressure': forms.TextInput(attrs={'placeholder': 'e.g., 120/80'}),
            'temperature': forms.NumberInput(attrs={'step': '0.1'}),
            'spo2': forms.NumberInput(attrs={'min': '0', 'max': '100'}),
            'pulse': forms.NumberInput(attrs={'min': '0', 'max': '300'}),
            'respirations': forms.NumberInput(attrs={'min': '0', 'max': '100'}),
            'pain': forms.NumberInput(attrs={'min': '0', 'max': '10'})
        }
        help_texts = {
            'blood_pressure': 'Enter as systolic/diastolic (e.g., 120/80)',
            'temperature': 'Temperature in Fahrenheit',
            'spo2': 'Oxygen saturation percentage',
            'pulse': 'Heart rate in beats per minute',
            'respirations': 'Breaths per minute',
            'supp_o2': 'Check if patient is on supplemental oxygen',
            'pain': 'Pain level (0-10)',
            'source': 'Source of vital signs information'
        }

    def validate_form_level_rules(self, cleaned_data):
        """Implement vital signs specific validation rules."""
        errors = {}
        
        # Validate blood pressure format
        bp = cleaned_data.get('blood_pressure')
        if bp:
            try:
                systolic, diastolic = map(int, bp.split('/'))
                if not (50 <= systolic <= 300 and 30 <= diastolic <= 200):
                    errors['blood_pressure'] = 'Blood pressure values out of normal range'
            except ValueError:
                errors['blood_pressure'] = 'Invalid blood pressure format'
        
        # Validate temperature range
        temp = cleaned_data.get('temperature')
        if temp and not (85 <= temp <= 110):
            errors['temperature'] = 'Temperature must be between 85°F and 110°F'
        
        # Validate oxygen saturation
        spo2 = cleaned_data.get('spo2')
        if spo2 and not (50 <= spo2 <= 100):
            errors['spo2'] = 'Oxygen saturation must be between 50% and 100%'
        
        # Validate pulse
        pulse = cleaned_data.get('pulse')
        if pulse and not (30 <= pulse <= 300):
            errors['pulse'] = 'Pulse must be between 30 and 300 beats per minute'
        
        # Validate respirations
        respirations = cleaned_data.get('respirations')
        if respirations and not (1 <= respirations <= 100):
            errors['respirations'] = 'Respirations must be between 1 and 100 breaths per minute'
        
        if errors:
            raise ValidationError(errors)

    def get_sections(self):
        """Define form sections for organized display."""
        return [
            {
                'title': 'Basic Vitals',
                'description': 'Enter basic vital signs',
                'fields': ['date', 'blood_pressure', 'temperature', 'pulse', 'respirations']
            },
            {
                'title': 'Oxygenation',
                'description': 'Enter oxygen-related measurements',
                'fields': ['spo2', 'supp_o2']
            },
            {
                'title': 'Assessment',
                'description': 'Enter additional assessments',
                'fields': ['pain', 'source']
            }
        ] 