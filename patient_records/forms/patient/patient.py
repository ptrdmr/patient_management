"""Patient form module."""

from django import forms
from django.forms import ModelForm
from django.utils import timezone
from django.core.exceptions import ValidationError
from ...models import Patient
from ..mixins.validation import DateValidationMixin, EventValidationMixin
from ...models.audit.constants import PATIENT_AGGREGATE


class PatientForm(DateValidationMixin, EventValidationMixin, ModelForm):
    """Form for patient registration and updates."""
    
    aggregate_type = PATIENT_AGGREGATE
    
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'max': timezone.now().date().isoformat(),
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = Patient
        fields = [
            'patient_number',
            'first_name',
            'middle_name',
            'last_name',
            'date_of_birth',
            'gender',
            'primary_provider',
            'address',
            'phone',
            'email',
            'emergency_contact',
            'insurance_info'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'emergency_contact': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'insurance_info': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'primary_provider': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'XXX-XXX-XXXX'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'patient_number': forms.TextInput(attrs={'class': 'form-control'})
        }
        help_texts = {
            'patient_number': 'External patient identifier',
            'primary_provider': 'Primary healthcare provider for this patient',
            'emergency_contact': 'Name and contact information for emergency contact',
            'insurance_info': 'Insurance provider and policy details'
        }

    def validate_event_consistency(self, latest_event, cleaned_data):
        """Validate that patient data is consistent with event history."""
        event_data = latest_event.event_data
        
        # Validate immutable fields
        if 'patient_number' in event_data:
            if cleaned_data.get('patient_number') != event_data['patient_number']:
                raise ValidationError({
                    'patient_number': 'Patient number cannot be changed once set'
                })
        
        # Validate date of birth hasn't changed
        if 'date_of_birth' in event_data:
            event_dob = event_data['date_of_birth']
            form_dob = cleaned_data.get('date_of_birth')
            if form_dob and form_dob.isoformat() != event_dob:
                raise ValidationError({
                    'date_of_birth': 'Date of birth cannot be changed once set'
                }) 