"""Search form module."""

from django import forms
from ..models import Patient
from django.utils import timezone

class PatientSearchForm(forms.Form):
    """Form for patient search and filtering."""
    
    # Basic search
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by name...',
            'class': 'form-control'
        })
    )
    
    # Patient ID search
    patient_id = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Patient ID',
            'class': 'form-control'
        })
    )
    
    # Demographics
    age_min = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Age'
        })
    )
    age_max = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Age'
        })
    )
    gender = forms.ChoiceField(
        choices=[('', '---')] + list(Patient.GENDER_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Date filters
    date_added_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    date_added_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    # Sort options
    sort_by = forms.ChoiceField(
        choices=[
            ('', '---'),
            ('last_name', 'Last Name'),
            ('first_name', 'First Name'),
            ('date_of_birth', 'Date of Birth'),
            ('-created_at', 'Last Added'),
            ('-updated_at', 'Last Updated'),
            ('patient_number', 'Patient ID')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Don't set any default values for date fields
        self.fields['date_added_from'].initial = None
        self.fields['date_added_to'].initial = None

    def has_filter_value(self, field_name):
        """Check if a field was explicitly set by the user."""
        value = self.cleaned_data.get(field_name)
        
        # Handle different types of empty values
        if value is None:
            return False
        if isinstance(value, str) and not value.strip():
            return False
        if isinstance(value, (list, dict, tuple)) and not value:
            return False
        
        return True

    def get_active_filters(self):
        """Return a dictionary of filters that are actually in use."""
        if not hasattr(self, 'cleaned_data'):
            return {}
            
        active_filters = {}
        for field_name, value in self.cleaned_data.items():
            if self.has_filter_value(field_name):
                # Strip whitespace from string values
                if isinstance(value, str):
                    value = value.strip()
                active_filters[field_name] = value
        return active_filters

    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        
        # Validate age range if both values are provided
        age_min = cleaned_data.get('age_min')
        age_max = cleaned_data.get('age_max')
        if age_min is not None and age_max is not None and age_min > age_max:
            raise forms.ValidationError('Minimum age cannot be greater than maximum age')
        
        # Validate date range if both values are provided
        date_from = cleaned_data.get('date_added_from')
        date_to = cleaned_data.get('date_added_to')
        
        today = timezone.now().date()
        
        # Only validate dates if they are actually provided
        if date_from:
            if date_from > today:
                self.add_error('date_added_from', 'Date cannot be in the future')
        
        if date_to:
            if date_to > today:
                self.add_error('date_added_to', 'Date cannot be in the future')
        
        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError('From date cannot be later than to date')
        
        return cleaned_data 