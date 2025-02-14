"""Records form module."""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from ...models import RecordRequestLog
from ..base import SectionedMedicalForm
from ...models.audit.constants import CLINICAL_AGGREGATE

class RecordRequestLogForm(SectionedMedicalForm):
    """Form for record request logging with enhanced validation and security."""
    
    aggregate_type = CLINICAL_AGGREGATE

    # Request types requiring immediate attention
    URGENT_REQUESTS = {
        'LEGAL': {
            'validation': 'Legal request - requires immediate processing',
            'max_days': 5
        },
        'EMERGENCY': {
            'validation': 'Emergency request - requires immediate processing',
            'max_days': 1
        },
        'TRANSFER': {
            'validation': 'Transfer request - requires timely processing',
            'max_days': 3
        }
    }
    
    class Meta:
        model = RecordRequestLog
        fields = [
            'date',
            'requester_name',
            'requester_organization',
            'request_type',
            'records_requested',
            'purpose',
            'due_date',
            'status',
            'notes',
            'source'
        ]
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'max': timezone.now().date().isoformat(),
                'class': 'form-control'
            }),
            'requester_name': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off'
            }),
            'requester_organization': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off'
            }),
            'request_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'records_requested': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'List specific records being requested'
            }),
            'purpose': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Purpose of the records request'
            }),
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Additional notes about the request'
            }),
            'source': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off'
            })
        }
        help_texts = {
            'date': 'Date when request was received',
            'requester_name': 'Name of person requesting records',
            'requester_organization': 'Organization making the request',
            'request_type': 'Type of request - urgent requests require immediate attention',
            'records_requested': 'Detailed list of requested records',
            'purpose': 'Purpose for requesting records',
            'due_date': 'When records need to be provided',
            'status': 'Current status of the request',
            'notes': 'Additional notes about processing the request',
            'source': 'How the request was received'
        }

    def clean(self):
        """Validate form data and relationships between fields."""
        cleaned_data = super().clean()
        
        # Validate request date is not in future
        date = cleaned_data.get('date')
        if date and date > timezone.now().date():
            raise ValidationError({
                'date': 'Request date cannot be in the future'
            })
        
        # Validate due date logic
        due_date = cleaned_data.get('due_date')
        request_type = cleaned_data.get('request_type')
        
        if due_date:
            if due_date <= date:
                raise ValidationError({
                    'due_date': 'Due date must be after request date'
                })
            
            # Check urgent request deadlines
            if request_type in self.URGENT_REQUESTS:
                max_days = self.URGENT_REQUESTS[request_type]['max_days']
                if (due_date - date).days > max_days:
                    raise ValidationError({
                        'due_date': f'{request_type} requests must be completed within {max_days} days'
                    })
        
        return cleaned_data

    def validate_form_level_rules(self, cleaned_data):
        """Implement request-specific validation rules."""
        warnings = []
        critical_alerts = []
        
        request_type = cleaned_data.get('request_type')
        records_requested = cleaned_data.get('records_requested', '')
        purpose = cleaned_data.get('purpose', '')
        
        # Check urgent requests
        if request_type in self.URGENT_REQUESTS:
            critical_alerts.append(
                f"URGENT REQUEST: {self.URGENT_REQUESTS[request_type]['validation']}"
            )
            self.instance.needs_attention = True
        
        # Validate records requested completeness
        if len(records_requested.split()) < 5:
            warnings.append(
                'Please provide more detailed description of requested records'
            )
        
        # Validate purpose completeness
        if len(purpose.split()) < 5:
            warnings.append(
                'Please provide more detailed purpose for the request'
            )
        
        # Raise validation messages
        errors = []
        if critical_alerts:
            errors.extend(['CRITICAL REQUEST ALERTS:', *critical_alerts])
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
                'title': 'Request Information',
                'description': 'Enter basic request details',
                'fields': ['date', 'requester_name', 'requester_organization', 'request_type']
            },
            {
                'title': 'Records Details',
                'description': 'Specify requested records and purpose',
                'fields': ['records_requested', 'purpose']
            },
            {
                'title': 'Processing Information',
                'description': 'Track request processing',
                'fields': ['due_date', 'status', 'notes']
            },
            {
                'title': 'Additional Information',
                'description': 'Enter any additional details',
                'fields': ['source']
            }
        ]

    def save(self, commit=True):
        """Save form with additional processing for urgent requests."""
        instance = super().save(commit=False)
        
        # Set needs_attention flag for urgent requests
        request_type = self.cleaned_data.get('request_type')
        instance.needs_attention = (
            request_type in self.URGENT_REQUESTS or
            instance.needs_attention  # Preserve any existing flags
        )
        
        if commit:
            instance.save()
            
        return instance 