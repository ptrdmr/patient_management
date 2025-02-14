"""Provider registration forms."""

from django import forms
from ...models import Provider
from ..base import SectionedMedicalForm
from ..mixins import PhoneValidationMixin, AddressValidationMixin, AuditFormMixin


class ProviderForm(SectionedMedicalForm, PhoneValidationMixin, AddressValidationMixin, AuditFormMixin):
    """Form for provider registration and updates."""

    class Meta:
        model = Provider
        fields = [
            'registration_date',
            'provider',
            'practice',
            'address',
            'city',
            'state',
            'zip_code',
            'fax',
            'phone',
            'source',
            'is_active'
        ]
        widgets = {
            'registration_date': forms.DateInput(attrs={'type': 'date'}),
            'phone': forms.TextInput(attrs={'placeholder': 'XXX-XXX-XXXX'}),
            'fax': forms.TextInput(attrs={'placeholder': 'XXX-XXX-XXXX'}),
            'zip_code': forms.TextInput(attrs={'placeholder': '12345 or 12345-6789'}),
            'state': forms.TextInput(attrs={'placeholder': 'XX', 'maxlength': '2'})
        }
        help_texts = {
            'phone': 'Enter as XXX-XXX-XXXX',
            'fax': 'Enter as XXX-XXX-XXXX (optional)',
            'zip_code': 'Enter as 12345 or 12345-6789',
            'state': 'Two-letter state code (e.g., CA)',
        }

    def get_sections(self):
        """Define form sections for organized display."""
        return [
            {
                'title': 'Provider Information',
                'fields': ['provider', 'practice', 'registration_date', 'is_active']
            },
            {
                'title': 'Contact Information',
                'fields': ['address', 'city', 'state', 'zip_code', 'phone', 'fax']
            },
            {
                'title': 'Additional Information',
                'fields': ['source']
            }
        ]

    def save(self, commit=True):
        """Override save to handle registration date."""
        instance = super().save(commit=False)
        if not instance.registration_date:
            instance.registration_date = datetime.date.today()
        if commit:
            instance.save()
        return instance 