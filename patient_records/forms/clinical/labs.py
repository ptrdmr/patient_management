"""Lab forms module."""

from django import forms
from django.core.exceptions import ValidationError
from ...models import CmpLabs, CbcLabs
from ..base import SectionedMedicalForm
from ..mixins.validation import DateValidationMixin

class CMPLabForm(SectionedMedicalForm, DateValidationMixin):
    """Form for Comprehensive Metabolic Panel (CMP) lab results with enhanced validation."""
    
    # Reference ranges for CMP values
    CMP_RANGES = {
        'sodium': {'min': 135, 'max': 145, 'unit': 'mEq/L'},
        'potassium': {'min': 3.5, 'max': 5.0, 'unit': 'mEq/L'},
        'chloride': {'min': 96, 'max': 106, 'unit': 'mEq/L'},
        'co2': {'min': 23, 'max': 29, 'unit': 'mEq/L'},
        'glucose': {'min': 70, 'max': 110, 'unit': 'mg/dL'},
        'bun': {'min': 7, 'max': 20, 'unit': 'mg/dL'},
        'creatinine': {'min': 0.6, 'max': 1.2, 'unit': 'mg/dL'},
        'calcium': {'min': 8.5, 'max': 10.5, 'unit': 'mg/dL'},
        'protein': {'min': 6.0, 'max': 8.0, 'unit': 'g/dL'},
        'albumin': {'min': 3.5, 'max': 5.0, 'unit': 'g/dL'},
        'bilirubin': {'min': 0.3, 'max': 1.2, 'unit': 'mg/dL'},
        'gfr': {'min': 60, 'max': None, 'unit': 'mL/min/1.73m²'}
    }
    
    class Meta:
        model = CmpLabs
        fields = [
            'date',
            'sodium',
            'potassium',
            'chloride',
            'co2',
            'glucose',
            'bun',
            'creatinine',
            'calcium',
            'protein',
            'albumin',
            'bilirubin',
            'gfr',
            'source'
        ]
        widgets = {
            'sodium': forms.NumberInput(attrs={'step': '0.1'}),
            'potassium': forms.NumberInput(attrs={'step': '0.1'}),
            'chloride': forms.NumberInput(attrs={'step': '0.1'}),
            'co2': forms.NumberInput(attrs={'step': '0.1'}),
            'glucose': forms.NumberInput(attrs={'step': '0.1'}),
            'bun': forms.NumberInput(attrs={'step': '0.1'}),
            'creatinine': forms.NumberInput(attrs={'step': '0.01'}),
            'calcium': forms.NumberInput(attrs={'step': '0.1'}),
            'protein': forms.NumberInput(attrs={'step': '0.1'}),
            'albumin': forms.NumberInput(attrs={'step': '0.1'}),
            'bilirubin': forms.NumberInput(attrs={'step': '0.1'}),
            'gfr': forms.NumberInput(attrs={'step': '1'})
        }
        help_texts = {
            'date': 'Date when labs were drawn',
            'source': 'Source of lab results',
            'sodium': 'Sodium level (mEq/L)',
            'potassium': 'Potassium level (mEq/L)',
            'chloride': 'Chloride level (mEq/L)',
            'co2': 'CO2 level (mEq/L)',
            'glucose': 'Glucose level (mg/dL)',
            'bun': 'Blood Urea Nitrogen (mg/dL)',
            'creatinine': 'Creatinine level (mg/dL)',
            'calcium': 'Calcium level (mg/dL)',
            'protein': 'Total protein (g/dL)',
            'albumin': 'Albumin level (g/dL)',
            'bilirubin': 'Total bilirubin (mg/dL)',
            'gfr': 'Glomerular Filtration Rate (mL/min/1.73m²)'
        }

    def validate_form_level_rules(self, cleaned_data):
        """Implement CMP-specific validation rules."""
        warnings = []
        
        # Check each lab value against reference ranges
        for field, value in cleaned_data.items():
            if field in self.CMP_RANGES and value is not None:
                ranges = self.CMP_RANGES[field]
                unit = ranges['unit']
                
                # Check minimum value
                if ranges['min'] is not None and value < ranges['min']:
                    warnings.append(
                        f"{field.title()}: {value} {unit} is below reference range "
                        f"(min: {ranges['min']} {unit})"
                    )
                
                # Check maximum value
                if ranges['max'] is not None and value > ranges['max']:
                    warnings.append(
                        f"{field.title()}: {value} {unit} is above reference range "
                        f"(max: {ranges['max']} {unit})"
                    )
        
        # Add warnings to non-field errors if any found
        if warnings:
            raise ValidationError({
                'non_field_errors': [
                    'The following values are outside normal ranges:',
                    *warnings
                ]
            })

    def get_sections(self):
        """Define form sections for organized display."""
        return [
            {
                'title': 'Basic Information',
                'description': 'Enter lab date and source',
                'fields': ['date', 'source']
            },
            {
                'title': 'Electrolytes',
                'description': 'Enter electrolyte values',
                'fields': ['sodium', 'potassium', 'chloride', 'co2']
            },
            {
                'title': 'Metabolic',
                'description': 'Enter metabolic values',
                'fields': ['glucose', 'bun', 'creatinine', 'gfr']
            },
            {
                'title': 'Proteins',
                'description': 'Enter protein values',
                'fields': ['protein', 'albumin', 'calcium', 'bilirubin']
            }
        ]


class CBCLabForm(SectionedMedicalForm):
    """Form for Complete Blood Count (CBC) lab results with enhanced validation."""
    
    # Reference ranges for CBC values
    CBC_RANGES = {
        'rbc': {'min': 4.0, 'max': 6.0, 'unit': 'M/µL'},
        'wbc': {'min': 4.0, 'max': 11.0, 'unit': 'K/µL'},
        'hemoglobin': {'min': 12.0, 'max': 17.0, 'unit': 'g/dL'},
        'hematocrit': {'min': 35.0, 'max': 50.0, 'unit': '%'},
        'mcv': {'min': 80.0, 'max': 100.0, 'unit': 'fL'},
        'mchc': {'min': 31.0, 'max': 37.0, 'unit': 'g/dL'},
        'rdw': {'min': 11.5, 'max': 14.5, 'unit': '%'},
        'platelets': {'min': 150.0, 'max': 450.0, 'unit': 'K/µL'},
        'mch': {'min': 27.0, 'max': 32.0, 'unit': 'pg'},
        'neutrophils': {'min': 40.0, 'max': 70.0, 'unit': '%'},
        'lymphocytes': {'min': 20.0, 'max': 40.0, 'unit': '%'},
        'monocytes': {'min': 2.0, 'max': 8.0, 'unit': '%'},
        'eosinophils': {'min': 1.0, 'max': 4.0, 'unit': '%'},
        'basophils': {'min': 0.5, 'max': 1.0, 'unit': '%'}
    }
    
    class Meta:
        model = CbcLabs
        fields = [
            'date',
            'rbc',
            'wbc',
            'hemoglobin',
            'hematocrit',
            'mcv',
            'mchc',
            'rdw',
            'platelets',
            'mch',
            'neutrophils',
            'lymphocytes',
            'monocytes',
            'eosinophils',
            'basophils',
            'source'
        ]
        widgets = {
            'rbc': forms.NumberInput(attrs={'step': '0.1'}),
            'wbc': forms.NumberInput(attrs={'step': '0.1'}),
            'hemoglobin': forms.NumberInput(attrs={'step': '0.1'}),
            'hematocrit': forms.NumberInput(attrs={'step': '0.1'}),
            'mcv': forms.NumberInput(attrs={'step': '0.1'}),
            'mchc': forms.NumberInput(attrs={'step': '0.1'}),
            'rdw': forms.NumberInput(attrs={'step': '0.1'}),
            'platelets': forms.NumberInput(attrs={'step': '1'}),
            'mch': forms.NumberInput(attrs={'step': '0.1'}),
            'neutrophils': forms.NumberInput(attrs={'step': '0.1'}),
            'lymphocytes': forms.NumberInput(attrs={'step': '0.1'}),
            'monocytes': forms.NumberInput(attrs={'step': '0.1'}),
            'eosinophils': forms.NumberInput(attrs={'step': '0.1'}),
            'basophils': forms.NumberInput(attrs={'step': '0.1'})
        }
        help_texts = {
            'date': 'Date when labs were drawn',
            'source': 'Source of lab results',
            'rbc': 'Red Blood Cell count (M/µL)',
            'wbc': 'White Blood Cell count (K/µL)',
            'hemoglobin': 'Hemoglobin level (g/dL)',
            'hematocrit': 'Hematocrit percentage (%)',
            'mcv': 'Mean Corpuscular Volume (fL)',
            'mchc': 'Mean Corpuscular Hemoglobin Concentration (g/dL)',
            'rdw': 'Red Cell Distribution Width (%)',
            'platelets': 'Platelet count (K/µL)',
            'mch': 'Mean Corpuscular Hemoglobin (pg)',
            'neutrophils': 'Neutrophil percentage (%)',
            'lymphocytes': 'Lymphocyte percentage (%)',
            'monocytes': 'Monocyte percentage (%)',
            'eosinophils': 'Eosinophil percentage (%)',
            'basophils': 'Basophil percentage (%)'
        }

    def validate_form_level_rules(self, cleaned_data):
        """Implement CBC-specific validation rules."""
        warnings = []
        critical_alerts = []
        
        # Check each lab value against reference ranges
        for field, value in cleaned_data.items():
            if field in self.CBC_RANGES and value is not None:
                ranges = self.CBC_RANGES[field]
                unit = ranges['unit']
                
                # Check minimum value
                if value < ranges['min']:
                    message = f"{field.title()}: {value} {unit} is below reference range (min: {ranges['min']} {unit})"
                    if value < ranges['min'] * 0.75:  # Critical threshold
                        critical_alerts.append(message)
                    else:
                        warnings.append(message)
                
                # Check maximum value
                if value > ranges['max']:
                    message = f"{field.title()}: {value} {unit} is above reference range (max: {ranges['max']} {unit})"
                    if value > ranges['max'] * 1.25:  # Critical threshold
                        critical_alerts.append(message)
                    else:
                        warnings.append(message)
        
        # Validate differential percentages sum to approximately 100%
        differential_fields = ['neutrophils', 'lymphocytes', 'monocytes', 'eosinophils', 'basophils']
        differential_sum = sum(cleaned_data.get(f, 0) or 0 for f in differential_fields)
        if all(cleaned_data.get(f) for f in differential_fields) and not 99 <= differential_sum <= 101:
            warnings.append(f"Differential percentages sum to {differential_sum}% (should be 100%)")
        
        # Raise validation errors
        errors = []
        if critical_alerts:
            errors.append('CRITICAL VALUES DETECTED:')
            errors.extend(critical_alerts)
        if warnings:
            errors.append('The following values are outside normal ranges:')
            errors.extend(warnings)
        
        if errors:
            raise ValidationError({
                'non_field_errors': errors
            })

    def get_sections(self):
        """Define form sections for organized display."""
        return [
            {
                'title': 'Basic Information',
                'description': 'Enter lab date and source',
                'fields': ['date', 'source']
            },
            {
                'title': 'Red Blood Cells',
                'description': 'Enter RBC-related values',
                'fields': ['rbc', 'hemoglobin', 'hematocrit', 'mcv', 'mchc', 'mch', 'rdw']
            },
            {
                'title': 'White Blood Cells',
                'description': 'Enter WBC-related values',
                'fields': ['wbc', 'neutrophils', 'lymphocytes', 'monocytes', 'eosinophils', 'basophils']
            },
            {
                'title': 'Platelets',
                'description': 'Enter platelet count',
                'fields': ['platelets']
            }
        ] 