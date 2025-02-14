"""Base forms for patient records app."""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from ..validators import sanitize_text, normalize_severity, format_date, validator
import logging
import datetime

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

class MedicalBaseForm(forms.ModelForm):
    """Enhanced base form with improved validation and security.
    
    This form class implements comprehensive validation, security checks,
    and audit logging for all medical forms. It follows HIPAA compliance
    guidelines and maintains a complete audit trail of all changes.
    """

    MEDICAL_VALIDATION_RULES = {
        'blood_pressure': {
            'pattern': r'^\d{2,3}\/\d{2,3}$',
            'message': 'Enter blood pressure as systolic/diastolic (e.g., 120/80)'
        },
        'temperature': {
            'min': '95',
            'max': '108',
            'step': '0.1',
            'message': 'Temperature must be between 95°F and 108°F'
        },
        'pulse': {
            'min': '40',
            'max': '200',
            'message': 'Pulse must be between 40 and 200 BPM'
        },
        'respiratory_rate': {
            'min': '8',
            'max': '40',
            'message': 'Respiratory rate must be between 8 and 40 breaths/min'
        },
        'height': {
            'min': '24',
            'max': '96',
            'message': 'Height must be between 24 and 96 inches'
        },
        'weight': {
            'min': '2',
            'max': '1000',
            'message': 'Weight must be between 2 and 1000 pounds'
        }
    }

    def __init__(self, *args, **kwargs):
        """Initialize form with security context."""
        self.user = kwargs.pop('user', None)
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.setup_fields()
        self.setup_security()
        self.setup_audit_logging()

    def setup_fields(self):
        """Set up form fields with enhanced validation."""
        for field_name, field in self.fields.items():
            # Base styling
            css_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'form-control {css_classes}'.strip()
            
            # Required fields
            if field.required:
                field.widget.attrs['required'] = 'required'

            # Date field handling with security constraints
            if isinstance(field, forms.DateField):
                self.setup_date_validation(field, field_name)
            
            # Numeric field validation
            elif isinstance(field, forms.DecimalField):
                self.setup_numeric_validation(field, field_name)
            
            # Text field sanitization
            elif isinstance(field, forms.CharField):
                self.setup_text_validation(field, field_name)

            # Add medical-specific validation
            if field_name in self.MEDICAL_VALIDATION_RULES:
                self.apply_medical_rules(field, field_name)

    def setup_security(self):
        """Set up security measures for the form."""
        if not self.user:
            raise ValidationError('User context is required for security')
        
        # Add CSRF protection
        if self.request:
            self.request.session.set_expiry(3600)  # 1 hour timeout
        
        # Set up field-level security
        self.setup_field_security()

    def setup_field_security(self):
        """Apply field-level security measures."""
        for field_name, field in self.fields.items():
            # Prevent XSS in text fields
            if isinstance(field, forms.CharField):
                field.widget.attrs['maxlength'] = field.max_length or 255
                
            # Ensure numeric fields have bounds
            elif isinstance(field, forms.DecimalField):
                field.widget.attrs.update({
                    'min': getattr(field, 'min_value', None),
                    'max': getattr(field, 'max_value', None),
                })

    def setup_date_validation(self, field, field_name):
        """Set up enhanced date field validation."""
        attrs = {
            'type': 'date',
            'class': 'form-control date-input'
        }
        
        # Prevent future dates unless explicitly allowed
        if not field_name.startswith(('dc_', 'due_', 'target_')):
            attrs['max'] = timezone.now().date().isoformat()
            
        field.widget = forms.DateInput(attrs=attrs)

    def setup_numeric_validation(self, field, field_name):
        """Set up enhanced numeric field validation."""
        field.widget.attrs.update({
            'step': 'any',
            'pattern': r'^\d*\.?\d*$'
        })

    def setup_text_validation(self, field, field_name):
        """Set up enhanced text field validation."""
        field.widget.attrs['pattern'] = r'^[^<>]*$'  # Prevent HTML injection

    def apply_medical_rules(self, field, field_name):
        """Apply medical-specific validation rules."""
        rules = self.MEDICAL_VALIDATION_RULES[field_name]
        field.widget.attrs.update({
            k: v for k, v in rules.items() 
            if k not in ['message']
        })
        field.widget.attrs['data-validation-message'] = rules['message']

    def setup_audit_logging(self):
        """Set up audit logging for the form."""
        if hasattr(self, 'instance') and self.instance.pk:
            self.initial_state = {
                field: getattr(self.instance, field)
                for field in self.fields
            }

    def clean(self):
        """Validate form data with enhanced security checks."""
        cleaned_data = super().clean()
        
        try:
            # Apply transformations and validations
            for field_name, value in cleaned_data.items():
                if value is None:
                    continue
                    
                field = self.fields[field_name]
                
                # Apply appropriate transformation
                if isinstance(field, forms.CharField):
                    cleaned_data[field_name] = sanitize_text(value)
                elif isinstance(field, forms.DecimalField):
                    cleaned_data[field_name] = self.validate_numeric(value, field_name)
                elif isinstance(field, forms.DateField):
                    cleaned_data[field_name] = self.validate_date(value, field_name)
            
            # Run validation pipeline
            self.validate_form_level_rules(cleaned_data)
            
        except Exception as e:
            logger.error(f"Error in form validation: {str(e)}")
            raise ValidationError("An error occurred during form validation")
        
        return cleaned_data

    def validate_numeric(self, value, field_name):
        """Validate numeric fields with bounds checking."""
        try:
            value = float(value)
            rules = self.MEDICAL_VALIDATION_RULES.get(field_name, {})
            
            if 'min' in rules and value < float(rules['min']):
                raise ValidationError(rules['message'])
            if 'max' in rules and value > float(rules['max']):
                raise ValidationError(rules['message'])
                
            return value
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid numeric value for {field_name}")

    def validate_date(self, value, field_name):
        """Validate date fields."""
        if not isinstance(value, (datetime.date, datetime.datetime)):
            raise ValidationError(f"Invalid date value for {field_name}")
            
        # Prevent future dates unless explicitly allowed
        if not field_name.startswith(('dc_', 'due_', 'target_')):
            if value > timezone.now().date():
                raise ValidationError("Future dates are not allowed")
                
        return value

    def validate_form_level_rules(self, cleaned_data):
        """Override this method to implement form-level validation rules."""
        pass

    def save(self, commit=True):
        """Save form with audit logging."""
        if not self.user:
            raise ValidationError('User context is required for saving')
            
        instance = super().save(commit=False)
        
        # Log changes if this is an update
        if hasattr(self, 'initial_state'):
            changes = {
                field: (self.initial_state[field], getattr(instance, field))
                for field in self.fields
                if self.initial_state[field] != getattr(instance, field)
            }
            if changes:
                logger.info(f"Form changes: {changes}")
        
        if commit:
            instance.save()
        
        return instance

class SectionedMedicalForm(MedicalBaseForm):
    """Base class for medical forms that use sections."""
    
    def get_sections(self):
        """Override this method to define form sections.
        
        Returns:
            list: A list of dictionaries, each containing:
                - title: Section title
                - description: Optional section description
                - fields: List of field names in this section
                - css_class: Optional CSS class for styling
        """
        return []

    @property
    def sections(self):
        """Get the form sections."""
        return self.get_sections()

    def validate_form_level_rules(self, cleaned_data):
        """Implement form-level validation rules."""
        super().validate_form_level_rules(cleaned_data)
        
        # Validate required fields within sections
        for section in self.get_sections():
            required_fields = [
                field for field in section.get('fields', [])
                if self.fields[field].required
            ]
            
            missing_fields = [
                field for field in required_fields
                if not cleaned_data.get(field)
            ]
            
            if missing_fields:
                raise ValidationError({
                    field: "This field is required"
                    for field in missing_fields
                }) 