from django import forms
from django.utils import timezone
from ..models import Symptoms, Provider
from .base import TransformableModelForm
from ..validators import normalize_severity

class SymptomsForm(TransformableModelForm):
    """Form for recording patient symptoms with data transformation"""
    
    # Add custom widgets and help text
    symptom = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter primary symptom'
        }),
        help_text="Enter the primary symptom or complaint"
    )
    
    severity = forms.IntegerField(
        required=False,
        widget=forms.Select(
            choices=[(None, '-- Select Severity --')] + list(Symptoms.SEVERITY_CHOICES),
            attrs={'class': 'form-control'}
        ),
        help_text="Select the severity level of the symptom"
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter any additional notes'
        }),
        help_text="Additional details about the symptom"
    )
    
    provider = forms.ModelChoiceField(
        queryset=Provider.objects.all().order_by('provider'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Select the healthcare provider if applicable"
    )
    
    class Meta:
        model = Symptoms
        fields = ['date', 'symptom', 'severity', 'notes', 'source', 'person_reporting', 'provider']
        widgets = {
            'date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),
            'source': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter information source'
                }
            ),
            'person_reporting': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter name of person reporting'
                }
            )
        }
    
    def clean_severity(self):
        """Custom cleaning for severity field"""
        severity = self.cleaned_data.get('severity')
        return normalize_severity(severity)
    
    def clean(self):
        """Additional form-wide validation"""
        cleaned_data = super().clean()
        
        # Ensure date is not in future
        date = cleaned_data.get('date')
        if date and date > timezone.now().date():
            self.add_error('date', 'Date cannot be in the future')
        
        # Ensure provider is valid if specified
        provider = cleaned_data.get('provider')
        if provider and not isinstance(provider, Provider):
            self.add_error('provider', 'Invalid provider selected')
        
        return cleaned_data 