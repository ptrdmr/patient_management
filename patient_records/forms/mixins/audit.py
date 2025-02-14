"""Form audit mixins."""

from django.utils import timezone
from ...models import AuditTrail


class AuditFormMixin:
    """Mixin for form audit logging."""

    def __init__(self, *args, **kwargs):
        """Initialize with user."""
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        """Save form and create audit trail."""
        instance = super().save(commit=False)
        
        # Determine if this is a new instance
        is_new = not bool(instance.pk)
        
        # Get the previous values if this is an update
        previous_values = {}
        if not is_new:
            previous_values = {
                field: getattr(instance, field)
                for field in self.changed_data
                if hasattr(instance, field)
            }
        
        if commit:
            instance.save()
        
        # Create audit trail entry
        if self.user:
            AuditTrail.objects.create(
                patient=getattr(instance, 'patient', None),
                patient_identifier=str(getattr(instance, 'patient', 'Unknown Patient')),
                action='CREATE' if is_new else 'UPDATE',
                record_type=instance._meta.model_name.upper(),
                user=self.user,
                previous_values=previous_values,
                new_values={
                    field: self.cleaned_data.get(field)
                    for field in self.changed_data
                }
            )
        
        return instance 