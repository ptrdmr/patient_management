from django import forms
from django.core.exceptions import ValidationError
from ..validators import sanitize_text, normalize_severity, format_date, validator
import logging

logger = logging.getLogger(__name__)

class TransformableModelForm(forms.ModelForm):
    """
    Base form class that provides data transformation capabilities
    """
    
    def clean(self):
        """
        Clean and transform the form data before validation
        """
        cleaned_data = super().clean()
        
        try:
            # Apply transformations based on field types
            for field_name, field in self.fields.items():
                value = cleaned_data.get(field_name)
                
                if value is None:
                    continue
                    
                # Transform text fields
                if isinstance(field, forms.CharField):
                    cleaned_data[field_name] = sanitize_text(value)
                
                # Transform severity fields
                elif isinstance(field, forms.IntegerField) and field_name == 'severity':
                    cleaned_data[field_name] = normalize_severity(value)
                
                # Transform date fields
                elif isinstance(field, forms.DateField) and value:
                    cleaned_data[field_name] = format_date(value)
            
            # Run the validation pipeline
            errors = validator.validate(cleaned_data)
            if errors:
                raise ValidationError({
                    'non_field_errors': errors
                })
                
        except Exception as e:
            logger.error(f"Error transforming form data: {str(e)}")
            raise ValidationError("An error occurred while processing the form data")
        
        return cleaned_data
    
    def _transform_text(self, value):
        """Transform text input"""
        return sanitize_text(value) if value else value
    
    def _transform_number(self, value):
        """Transform numeric input"""
        try:
            return float(value) if value else None
        except (ValueError, TypeError):
            return None
    
    def _transform_date(self, value):
        """Transform date input"""
        return format_date(value) if value else None
    
    class Meta:
        abstract = True 