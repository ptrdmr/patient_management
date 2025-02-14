"""Patient update form module."""

from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from ...models import Patient
from ..mixins.validation import DateValidationMixin, EventValidationMixin
from ...models.audit.constants import PATIENT_AGGREGATE


class PatientUpdateForm(DateValidationMixin, EventValidationMixin, ModelForm):
    """Form for updating existing patient information.
    
    This form specifically handles updates to patient records, with proper
    validation to ensure immutable fields cannot be changed and that all
    changes are properly audited.
    """
    
    aggregate_type = PATIENT_AGGREGATE
    
    class Meta:
        model = Patient
        fields = [
            'first_name',
            'middle_name',
            'last_name',
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
            'primary_provider': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'XXX-XXX-XXXX'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'})
        }
        help_texts = {
            'primary_provider': 'Primary healthcare provider for this patient',
            'emergency_contact': 'Name and contact information for emergency contact',
            'insurance_info': 'Insurance provider and policy details'
        }

    def __init__(self, *args, **kwargs):
        """Initialize the form with additional security checks."""
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.setup_audit_logging()

    def setup_audit_logging(self):
        """Set up audit logging for the form."""
        if not hasattr(self, 'instance') or not self.instance.pk:
            raise ValidationError('Update form requires an existing patient instance')

    def clean(self):
        """Validate the form data."""
        cleaned_data = super().clean()
        
        # Ensure critical fields are not empty
        required_fields = ['first_name', 'last_name', 'phone']
        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, 'This field is required for updates')
        
        return cleaned_data

    def validate_event_consistency(self, latest_event, cleaned_data):
        """Validate that patient data is consistent with event history."""
        if not latest_event:
            raise ValidationError('Cannot update patient without event history')
        
        event_data = latest_event.event_data
        
        # Validate any business rules for updates
        # Add specific validation rules here as needed
        pass

    def save(self, commit=True):
        """Save the form with proper audit trail."""
        if not self.user:
            raise ValidationError('User is required for patient updates')
            
        patient = super().save(commit=False)
        
        if commit:
            patient.save()
            
            # Create audit trail
            from ...models import AuditTrail
            AuditTrail.objects.create(
                patient=patient,
                action='UPDATE',
                user=self.user,
                record_type='Patient',
                previous_values=self.initial,
                new_values=self.cleaned_data
            )
            
        return patient 