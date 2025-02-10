"""Provider model definition."""

from django.db import models
from ..base import BaseModel
import datetime


class Provider(BaseModel):
    """Provider model representing a healthcare provider."""

    registration_date = models.DateField(
        help_text="Date when provider was registered in the system",
        default=datetime.date.today
    )
    provider = models.CharField(max_length=100, help_text="Provider's full name")
    practice = models.CharField(max_length=200, help_text="Name of the medical practice")
    address = models.CharField(max_length=255, help_text="Street address")
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2, help_text="Two-letter US state code")
    zip_code = models.CharField(max_length=10, help_text="US ZIP code (5 or 9 digits)")
    fax = models.CharField(max_length=20, blank=True, null=True, help_text="Format: XXX-XXX-XXXX")
    phone = models.CharField(max_length=20, help_text="Format: XXX-XXX-XXXX")
    source = models.CharField(max_length=100, blank=True, null=True, help_text="Data source system")
    is_active = models.BooleanField(default=True, help_text="Whether the provider is currently active")

    class Meta:
        indexes = [
            models.Index(fields=['provider']),
            models.Index(fields=['practice']),
            models.Index(fields=['-registration_date']),
            models.Index(fields=['state']),
            models.Index(fields=['is_active'])
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(state__regex=r'^[A-Z]{2}$'),
                name='provider_state_format'
            ),
            models.CheckConstraint(
                check=models.Q(zip_code__regex=r'^\d{5}(-\d{4})?$'),
                name='provider_zip_format'
            ),
            models.CheckConstraint(
                check=models.Q(phone__regex=r'^\d{3}-\d{3}-\d{4}$'),
                name='provider_phone_format'
            ),
            models.CheckConstraint(
                check=models.Q(fax__isnull=True) | models.Q(fax__regex=r'^\d{3}-\d{3}-\d{4}$'),
                name='provider_fax_format'
            )
        ]

    def clean(self):
        """Clean and validate provider data."""
        # Normalize state to uppercase
        if self.state:
            self.state = self.state.upper()

        # Normalize phone format
        if self.phone and len(self.phone.replace('-', '')) == 10:
            phone_digits = self.phone.replace('-', '')
            self.phone = f"{phone_digits[:3]}-{phone_digits[3:6]}-{phone_digits[6:]}"

        # Normalize fax format
        if self.fax and len(self.fax.replace('-', '')) == 10:
            fax_digits = self.fax.replace('-', '')
            self.fax = f"{fax_digits[:3]}-{fax_digits[3:6]}-{fax_digits[6:]}"

    def __str__(self):
        """Return string representation of the provider."""
        return f"{self.provider} ({self.practice})" 