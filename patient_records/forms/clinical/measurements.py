"""Measurements form module."""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from ...models import Measurements
from ..base import SectionedMedicalForm
from ...models.audit.constants import CLINICAL_AGGREGATE

class MeasurementsForm(SectionedMedicalForm):
    """Form for patient measurements with enhanced validation and safety features."""
    
    aggregate_type = CLINICAL_AGGREGATE

    # Reference ranges and validation rules
    MEASUREMENT_RANGES = {
        'weight': {
            'min': 1.0,
            'max': 1000.0,
            'unit': 'lbs',
            'significant_change': 5.0  # % change that requires attention
        },
        'mac': {
            'min': 10.0,
            'max': 50.0,
            'unit': 'cm',
            'significant_change': 10.0
        },
        'pps': {
            'min': 0,
            'max': 100,
            'unit': '%',
            'significant_change': 20.0
        }
    }

    # Critical thresholds that require immediate attention
    CRITICAL_THRESHOLDS = {
        'weight_loss': {
            'threshold': 5.0,  # % loss in 30 days
            'message': 'Significant weight loss detected'
        },
        'pps_decline': {
            'threshold': 20.0,  # % decline
            'message': 'Significant PPS decline detected'
        },
        'nutritional_risk': {
            'values': ['Poor', 'Very Poor'],
            'message': 'Poor nutritional intake reported'
        }
    }
    
    class Meta:
        model = Measurements
        fields = [
            'date',
            'weight',
            'value',
            'nutritional_intake',
            'mac',
            'fast',
            'pps',
            'plof',
            'source'
        ]
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'max': timezone.now().date().isoformat(),
                'class': 'form-control'
            }),
            'weight': forms.NumberInput(attrs={
                'step': '0.1',
                'class': 'form-control',
                'placeholder': 'Enter weight in pounds'
            }),
            'value': forms.NumberInput(attrs={
                'step': '0.1',
                'class': 'form-control'
            }),
            'nutritional_intake': forms.Select(attrs={
                'class': 'form-control'
            }),
            'mac': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter in centimeters'
            }),
            'fast': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'pps': forms.NumberInput(attrs={
                'min': '0',
                'max': '100',
                'class': 'form-control',
                'placeholder': 'Enter 0-100'
            }),
            'plof': forms.Select(attrs={
                'class': 'form-control'
            }),
            'source': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off'
            })
        }
        help_texts = {
            'date': 'Date when measurements were taken',
            'weight': 'Patient weight in pounds - significant changes will be flagged',
            'value': 'Additional value measurement if needed',
            'nutritional_intake': 'Assessment of nutritional intake status',
            'mac': 'Mid-arm circumference in centimeters',
            'fast': 'Functional Assessment Screening Tool score',
            'pps': 'Palliative Performance Scale (0-100%)',
            'plof': 'Prior Level of Function assessment',
            'source': 'Source of measurement information (e.g., direct measurement, reported)'
        }

    def clean_weight(self):
        """Validate weight and check for significant changes."""
        weight = self.cleaned_data.get('weight')
        if weight is None:
            return weight

        # Validate range
        if weight < self.MEASUREMENT_RANGES['weight']['min']:
            raise ValidationError(f"Weight cannot be less than {self.MEASUREMENT_RANGES['weight']['min']} lbs")
        if weight > self.MEASUREMENT_RANGES['weight']['max']:
            raise ValidationError(f"Weight cannot exceed {self.MEASUREMENT_RANGES['weight']['max']} lbs")

        # Check for significant changes if this isn't the first measurement
        if self.instance.patient:
            previous = Measurements.objects.filter(
                patient=self.instance.patient,
                date__lt=self.cleaned_data.get('date')
            ).order_by('-date').first()

            if previous and previous.weight:
                change = abs((weight - previous.weight) / previous.weight * 100)
                if change >= self.MEASUREMENT_RANGES['weight']['significant_change']:
                    self.instance.needs_attention = True

        return weight

    def clean_pps(self):
        """Validate PPS score and check for significant decline."""
        pps = self.cleaned_data.get('pps')
        if pps is None:
            return pps

        # Validate range
        if not (0 <= pps <= 100):
            raise ValidationError("PPS must be between 0 and 100")

        # Check for significant decline if this isn't the first measurement
        if self.instance.patient:
            previous = Measurements.objects.filter(
                patient=self.instance.patient,
                date__lt=self.cleaned_data.get('date')
            ).order_by('-date').first()

            if previous and previous.pps:
                decline = previous.pps - pps
                if decline >= self.CRITICAL_THRESHOLDS['pps_decline']['threshold']:
                    self.instance.needs_attention = True

        return pps

    def validate_form_level_rules(self, cleaned_data):
        """Implement measurement-specific validation rules."""
        warnings = []
        critical_alerts = []
        
        # Check nutritional intake
        nutritional_intake = cleaned_data.get('nutritional_intake')
        if nutritional_intake in self.CRITICAL_THRESHOLDS['nutritional_risk']['values']:
            critical_alerts.append(
                f"ATTENTION: {self.CRITICAL_THRESHOLDS['nutritional_risk']['message']}"
            )
            self.instance.needs_attention = True

        # Validate MAC if provided
        mac = cleaned_data.get('mac')
        if mac:
            try:
                mac_value = float(mac.split()[0])  # Extract numeric value
                if not (self.MEASUREMENT_RANGES['mac']['min'] <= mac_value <= self.MEASUREMENT_RANGES['mac']['max']):
                    warnings.append(
                        f"MAC measurement ({mac}) is outside normal range "
                        f"({self.MEASUREMENT_RANGES['mac']['min']}-{self.MEASUREMENT_RANGES['mac']['max']} cm)"
                    )
            except (ValueError, IndexError):
                warnings.append("MAC should be entered as a number followed by 'cm'")

        # Validate date is not in future
        date = cleaned_data.get('date')
        if date and date > timezone.now().date():
            raise ValidationError({
                'date': 'Measurement date cannot be in the future'
            })

        # Raise validation messages
        errors = []
        if critical_alerts:
            errors.extend(['CRITICAL ALERTS:', *critical_alerts])
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
                'title': 'Basic Measurements',
                'description': 'Enter primary measurements - significant changes will be flagged',
                'fields': ['date', 'weight', 'value']
            },
            {
                'title': 'Nutritional Assessment',
                'description': 'Enter nutritional status information',
                'fields': ['nutritional_intake', 'mac']
            },
            {
                'title': 'Functional Assessment',
                'description': 'Enter functional assessment scores - significant changes will be monitored',
                'fields': ['fast', 'pps', 'plof']
            },
            {
                'title': 'Source',
                'description': 'Enter measurement source information',
                'fields': ['source']
            }
        ] 