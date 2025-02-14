"""Form validation mixins."""

import re
from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from ...models import EventStore


class PhoneValidationMixin:
    """Mixin for phone number validation."""

    def clean_phone(self):
        """Clean and format phone number."""
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove any non-digit characters
            cleaned = ''.join(filter(str.isdigit, phone))
            if len(cleaned) != 10:
                raise forms.ValidationError('Phone number must be 10 digits')
            # Format as XXX-XXX-XXXX
            return f"{cleaned[:3]}-{cleaned[3:6]}-{cleaned[6:]}"
        return phone

    def clean_fax(self):
        """Clean and format fax number."""
        fax = self.cleaned_data.get('fax')
        if fax:
            # Remove any non-digit characters
            cleaned = ''.join(filter(str.isdigit, fax))
            if len(cleaned) != 10:
                raise forms.ValidationError('Fax number must be 10 digits')
            # Format as XXX-XXX-XXXX
            return f"{cleaned[:3]}-{cleaned[3:6]}-{cleaned[6:]}"
        return fax


class AddressValidationMixin:
    """Mixin for address field validation."""

    def clean_state(self):
        """Clean and validate state code."""
        state = self.cleaned_data.get('state')
        if state:
            state = state.upper()
            if not re.match(r'^[A-Z]{2}$', state):
                raise forms.ValidationError('State must be a two-letter code')
            return state
        return state

    def clean_zip_code(self):
        """Clean and validate ZIP code."""
        zip_code = self.cleaned_data.get('zip_code')
        if zip_code:
            # Remove any non-digit characters
            cleaned = ''.join(filter(str.isdigit, zip_code))
            if len(cleaned) == 5:
                return cleaned
            elif len(cleaned) == 9:
                return f"{cleaned[:5]}-{cleaned[5:]}"
            raise forms.ValidationError('ZIP code must be 5 or 9 digits')
        return zip_code


class DateValidationMixin:
    """Mixin for date field validation."""

    def clean(self):
        """Validate all date fields are not in the future."""
        cleaned_data = super().clean()
        if not cleaned_data:
            return cleaned_data
            
        today = timezone.now().date()
        
        # Get all date fields from the form
        date_fields = [
            field_name for field_name, field in self.fields.items()
            if isinstance(field, forms.DateField)
            and not field_name.startswith(('dc_', 'due_', 'target_', 'follow_up_'))
        ]
        
        # Validate each date field
        for field_name in date_fields:
            date = cleaned_data.get(field_name)
            if date and date > today:
                self.add_error(field_name, 'Future dates are not allowed.')
                cleaned_data.pop(field_name, None)
        
        return cleaned_data


class EventValidationMixin:
    """Mixin for validating event-sourced data."""

    def clean(self):
        """Validate event data consistency."""
        cleaned_data = super().clean()
        if not cleaned_data:
            return cleaned_data

        # Get the aggregate type and ID if they exist in the form
        aggregate_type = getattr(self, 'aggregate_type', None)
        aggregate_id = cleaned_data.get('id') or getattr(self.instance, 'id', None)

        if aggregate_type and aggregate_id:
            # Check if there are any existing events for this aggregate
            latest_event = EventStore.objects.filter(
                aggregate_type=aggregate_type,
                aggregate_id=str(aggregate_id)
            ).order_by('-sequence').first()

            if latest_event:
                # Validate that the current state matches the event history
                self.validate_event_consistency(latest_event, cleaned_data)

        return cleaned_data

    def validate_event_consistency(self, latest_event, cleaned_data):
        """
        Validate that the current form data is consistent with event history.
        Override this method in specific form classes to implement custom validation.
        """
        pass 