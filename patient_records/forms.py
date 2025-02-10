"""Forms for patient records app."""

from django import forms
from django.forms import ModelForm
from django.utils import timezone
import datetime
import re

from .widgets import ICDCodeWidget, PhoneNumberWidget
from .models import (
    Patient,
    Provider,
    Vitals,
    CmpLabs,
    CbcLabs,
    ClinicalNotes,
    PatientNote,
    NoteTag,
    NoteAttachment,
    Measurements,
    Symptoms,
    Imaging,
    Adls,
    Occurrences,
    Diagnosis,
    Visits,
    Medications,
    RecordRequestLog
)

# Move these base classes to the top of the file
class BaseForm(forms.ModelForm):
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
        super().__init__(*args, **kwargs)
        self.setup_fields()

    def setup_fields(self):
        """Add common attributes and validation rules to fields"""
        for field_name, field in self.fields.items():
            # Existing attributes
            css_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'form-control {css_classes}'.strip()
            
            # Add validation rules based on field type
            if field.required:
                field.widget.attrs['required'] = 'required'

            # Date field handling
            if isinstance(field, forms.DateField):
                field.widget = forms.DateInput(
                    attrs={
                        'type': 'date',
                        'class': 'form-control date-input',
                        'max': datetime.date.today().isoformat() if not field_name.startswith(('dc_', 'due_', 'target_')) else None
                    }
                )
            
            # Phone field handling
            if field_name in ['phone', 'fax', 'mobile', 'emergency_phone', 
                             'work_phone', 'home_phone', 'patient_phone', 
                             'poa_contact']:
                field.widget = PhoneNumberWidget(
                    attrs=field.widget.attrs,
                    country_selector=True if field_name in ['phone', 'patient_phone'] else False
                )

            # Add field-specific validation
            if field_name == 'ssn':
                field.widget.attrs['pattern'] = r'^\d{3}-?\d{2}-?\d{4}$'
                field.widget.attrs['data-validation-message'] = 'Please enter a valid SSN (XXX-XX-XXXX)'
            
            # Add medical-specific validation
            if field_name in self.MEDICAL_VALIDATION_RULES:
                rules = self.MEDICAL_VALIDATION_RULES[field_name]
                
                if 'pattern' in rules:
                    field.widget.attrs['pattern'] = rules['pattern']
                if 'min' in rules:
                    field.widget.attrs['min'] = rules['min']
                if 'max' in rules:
                    field.widget.attrs['max'] = rules['max']
                if 'step' in rules:
                    field.widget.attrs['step'] = rules['step']
                
                field.widget.attrs['data-validation-message'] = rules['message']

    @property
    def sections(self):
        """Override this in form classes that need sections"""
        return None

class SectionedForm(BaseForm):
    """Base class for forms that use sections"""
    
    def get_sections(self):
        """Override this method to define form sections"""
        return []

    @property
    def sections(self):
        return self.get_sections()

# Then your existing form classes follow...
class ProviderForm(SectionedForm):
    class Meta:
        model = Provider
        fields = ['registration_date', 'provider', 'practice', 'address', 'city', 'state', 'zip_code', 'fax', 'phone', 'source', 'is_active']
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

    def clean_phone(self):
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
        fax = self.cleaned_data.get('fax')
        if fax:
            # Remove any non-digit characters
            cleaned = ''.join(filter(str.isdigit, fax))
            if len(cleaned) != 10:
                raise forms.ValidationError('Fax number must be 10 digits')
            # Format as XXX-XXX-XXXX
            return f"{cleaned[:3]}-{cleaned[3:6]}-{cleaned[6:]}"
        return fax

    def clean_state(self):
        state = self.cleaned_data.get('state')
        if state:
            state = state.upper()
            if not re.match(r'^[A-Z]{2}$', state):
                raise forms.ValidationError('State must be a two-letter code')
            return state
        return state

    def clean_zip_code(self):
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

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.registration_date:
            instance.registration_date = datetime.date.today()
        if commit:
            instance.save()
        return instance

class DiagnosisForm(SectionedForm):
    class Meta:
        model = Diagnosis
        fields = ['icd_code', 'diagnosis', 'date', 'notes', 'source']
        widgets = {
            'icd_code': ICDCodeWidget(attrs={
                'placeholder': 'Enter ICD code',
                'data-diagnosis-field': 'diagnosis'
            }),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'diagnosis': forms.TextInput(attrs={'placeholder': 'Enter diagnosis'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter any additional notes'}),
            'source': forms.TextInput(attrs={'placeholder': 'Enter source of diagnosis'})
        }

    def get_sections(self):
        return [
            {
                'title': 'Diagnosis Information',
                'description': 'Enter diagnosis details',
                'fields': ['icd_code', 'diagnosis', 'date', 'notes', 'source']
            }
        ]

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date > timezone.now().date():
            raise forms.ValidationError('Future dates are not allowed.')
        return date

class VisitsForm(BaseForm):
    class Meta:
        model = Visits
        fields = [
            'date', 'visit_type', 'provider', 'practice',
            'chief_complaint', 'assessment', 'plan',
            'notes', 'source'
        ]

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date > timezone.now().date():
            raise forms.ValidationError('Future dates are not allowed.')
        return date

    def get_sections(self):
        return [
            {
                'title': 'Visit Information',
                'description': 'Basic visit details',
                'fields': ['date', 'visit_type', 'provider']
            },
            {
                'title': 'Clinical Information',
                'description': 'Clinical assessment and plan',
                'fields': ['chief_complaint', 'assessment', 'plan']
            },
            {
                'title': 'Location & Details',
                'description': 'Where the visit took place',
                'fields': ['practice', 'notes']
            },
            {
                'title': 'Additional Information',
                'description': 'Source information',
                'fields': ['source']
            }
        ]

class VitalsForm(SectionedForm):
    class Meta:
        model = Vitals
        fields = ['date', 'blood_pressure', 'temperature', 'spo2', 'pulse', 
                 'respirations', 'supp_o2', 'pain', 'source']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'blood_pressure': forms.TextInput(attrs={
                'placeholder': '120/80',
                'pattern': r'^\d{2,3}\/\d{2,3}$'
            }),
            'spo2': forms.NumberInput(attrs={
                'min': '0',
                'max': '100',
                'step': '1'
            }),
            'pain': forms.NumberInput(attrs={
                'min': '0',
                'max': '10',
                'step': '1'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['blood_pressure'].help_text = 'Enter as systolic/diastolic (e.g., 120/80)'
        self.fields['spo2'].help_text = 'Oxygen saturation percentage (0-100)'
        self.fields['pain'].help_text = 'Pain scale 0-10'

    def get_sections(self):
        return [
            {
                'title': 'Basic Information',
                'description': 'Date and source of vital signs',
                'fields': ['date', 'source']
            },
            {
                'title': 'Vital Measurements',
                'description': 'Core vital sign measurements',
                'fields': ['blood_pressure', 'temperature', 'pulse', 'respirations']
            },
            {
                'title': 'Oxygenation',
                'description': 'Oxygen saturation and supplementation',
                'fields': ['spo2', 'supp_o2']
            },
            {
                'title': 'Additional Assessments',
                'description': 'Pain and other measurements',
                'fields': ['pain']
            }
        ]

class CMPLabForm(SectionedForm):
    class Meta:
        model = CmpLabs
        fields = [
            'date', 'sodium', 'potassium', 'chloride', 'co2', 'bun', 
            'creatinine', 'glucose', 'calcium', 'protein', 'albumin', 
            'bilirubin', 'gfr'
        ]

    def get_sections(self):
        return [
            {
                'title': 'Basic Information',
                'fields': ['date']
            },
            {
                'title': 'Electrolytes',
                'fields': ['sodium', 'potassium', 'chloride', 'co2']
            },
            {
                'title': 'Kidney Function',
                'fields': ['bun', 'creatinine', 'gfr']
            },
            {
                'title': 'Metabolic Panel',
                'fields': ['glucose', 'calcium', 'protein', 'albumin']
            },
            {
                'title': 'Liver Function',
                'fields': ['bilirubin']
            }
        ]

class CBCLabForm(SectionedForm):
    class Meta:
        model = CbcLabs
        fields = [
            'date', 'wbc', 'rbc', 'hemoglobin', 'hematocrit', 'mcv', 
            'mch', 'mchc', 'rdw', 'platelets', 'neutrophils', 
            'lymphocytes', 'monocytes', 'eosinophils', 'basophils'
        ]

    def get_sections(self):
        return [
            {
                'title': 'Basic Information',
                'fields': ['date']
            },
            {
                'title': 'Red Blood Cell Panel',
                'fields': ['rbc', 'hemoglobin', 'hematocrit']
            },
            {
                'title': 'Red Blood Cell Indices',
                'fields': ['mcv', 'mch', 'mchc', 'rdw']
            },
            {
                'title': 'White Blood Cell Panel',
                'fields': ['wbc', 'neutrophils', 'lymphocytes', 'monocytes', 'eosinophils', 'basophils']
            },
            {
                'title': 'Platelets',
                'fields': ['platelets']
            }
        ]

class SymptomsForm(SectionedForm):
    class Meta:
        model = Symptoms
        fields = ['date', 'symptom', 'notes', 'source', 'person_reporting']

    def get_sections(self):
        return [
            {
                'title': 'Symptom Information',
                'description': 'Primary symptom details',
                'fields': ['date', 'symptom']
            },
            {
                'title': 'Additional Details',
                'description': 'Notes and source information',
                'fields': ['notes', 'source', 'person_reporting']
            }
        ]

class MedicationsForm(SectionedForm):
    class Meta:
        model = Medications
        fields = ['date_prescribed', 'drug', 'dose', 'route', 'frequency', 'prn', 'dc_date', 'notes']
        help_texts = {
            'dc_date': 'Leave blank if medication is currently active. Only fill this in when discontinuing the medication.',
            'prn': 'Check this box if the medication is to be taken as needed.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override the base form's date field handling
        self.fields['dc_date'].required = False
        self.fields['dc_date'].initial = None
        
        # Completely override the date input widgets
        self.fields['date_prescribed'].widget = forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control date-input',
                'max': datetime.date.today().isoformat()
            }
        )
        self.fields['dc_date'].widget = forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control date-input'
            }
        )
        
        # Set today's date for date_prescribed
        self.fields['date_prescribed'].initial = datetime.date.today()

    def clean(self):
        """Clean and validate form data."""
        cleaned_data = super().clean()
        date_prescribed = cleaned_data.get('date_prescribed')
        dc_date = cleaned_data.get('dc_date')

        if date_prescribed and dc_date and dc_date < date_prescribed:
            self.add_error('dc_date', 'Discontinue date cannot be earlier than the prescribed date.')

        return cleaned_data

    def get_sections(self):
        return [
            {
                'title': 'Medication Details',
                'description': 'Basic medication information',
                'fields': ['date_prescribed', 'drug', 'dose']
            },
            {
                'title': 'Administration',
                'description': 'How the medication is given',
                'fields': ['route', 'frequency', 'prn']
            },
            {
                'title': 'Additional Information',
                'description': 'Other relevant details',
                'fields': ['dc_date', 'notes']
            }
        ]

class MeasurementsForm(SectionedForm):
    class Meta:
        model = Measurements
        fields = ['date', 'weight', 'nutritional_intake', 'mac', 'fast', 'pps', 'plof', 'source']

    def get_sections(self):
        return [
            {
                'title': 'Basic Measurements',
                'description': 'Primary measurements',
                'fields': ['date', 'weight']
            },
            {
                'title': 'Nutritional Assessment',
                'description': 'Nutrition-related measurements',
                'fields': ['nutritional_intake', 'mac']
            },
            {
                'title': 'Performance Metrics',
                'description': 'Functional assessments',
                'fields': ['fast', 'pps', 'plof']
            },
            {
                'title': 'Additional Information',
                'description': 'Source information',
                'fields': ['source']
            }
        ]

class AdlsForm(SectionedForm):
    class Meta:
        model = Adls
        fields = ['date', 'ambulation', 'continence', 'transfer', 'dressing', 'feeding', 'bathing', 'notes', 'source']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

    def get_sections(self):
        return [
            {
                'title': 'Assessment Date',
                'description': 'When the assessment was performed',
                'fields': ['date']
            },
            {
                'title': 'Mobility & Movement',
                'description': 'Movement-related activities',
                'fields': ['ambulation', 'transfer']
            },
            {
                'title': 'Self-Care Activities',
                'description': 'Personal care activities',
                'fields': ['dressing', 'feeding', 'bathing', 'continence']
            },
            {
                'title': 'Additional Information',
                'description': 'Notes and source',
                'fields': ['notes', 'source']
            }
        ]

class ImagingForm(SectionedForm):
    class Meta:
        model = Imaging
        fields = ['date', 'type', 'notes', 'source']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

    def get_sections(self):
        return [
            {
                'title': 'Study Information',
                'description': 'Basic imaging details',
                'fields': ['date', 'type']
            },
            {
                'title': 'Results & Notes',
                'description': 'Study findings and additional information',
                'fields': ['notes']
            },
            {
                'title': 'Additional Information',
                'description': 'Source information',
                'fields': ['source']
            }
        ]

class OccurrencesForm(SectionedForm):
    class Meta:
        model = Occurrences
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

    def get_sections(self):
        return [
            {
                'title': 'Event Information',
                'description': 'When and what happened',
                'fields': ['date', 'time', 'occurrence_type']
            },
            {
                'title': 'Event Details',
                'description': 'Detailed information about the occurrence',
                'fields': ['severity', 'location', 'witnesses']
            },
            {
                'title': 'Response & Follow-up',
                'description': 'Actions taken and additional notes',
                'fields': ['action_taken', 'staff_response', 'follow_up_needed', 'notes']
            }
        ]

class RecordRequestLogForm(SectionedForm):
    class Meta:
        model = RecordRequestLog
        fields = ['date', 'request_type', 'purpose', 'records_requested', 'source']

    def get_sections(self):
        return [
            {
                'title': 'Request Information',
                'description': 'Basic request details',
                'fields': ['date', 'request_type', 'purpose']
            },
            {
                'title': 'Records Information',
                'description': 'Details about the requested records',
                'fields': ['records_requested', 'source']
            }
        ]

class PatientForm(ModelForm):
    class Meta:
        model = Patient
        fields = [
            'patient_number',
            'first_name',
            'middle_name',
            'last_name',
            'date_of_birth',
            'gender',
            'address',
            'phone',
            'email',
            'emergency_contact',
            'insurance_info'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'emergency_contact': forms.Textarea(attrs={'rows': 3}),
            'insurance_info': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'patient_number': 'External patient identifier',
            'emergency_contact': 'Name and contact information for emergency contact',
            'insurance_info': 'Insurance provider and policy details'
        }

class PatientNoteForm(SectionedForm):
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter tags separated by commas'
        })
    )

    class Meta:
        model = PatientNote
        fields = ['patient', 'title', 'content', 'category', 'tags', 'is_pinned']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5, 'class': 'note-content'}),
            'patient': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_pinned'].widget.attrs['class'] = 'form-check-input'
        self.fields['patient'].required = True

        # Convert tags to comma-separated string if instance exists
        if self.instance.pk and self.instance.tags.exists():
            self.initial['tags'] = ', '.join(tag.name for tag in self.instance.tags.all())

    def clean_tags(self):
        """Convert comma-separated tags string to list of tag names"""
        tags = self.cleaned_data.get('tags', '')
        if tags:
            # Split by comma, strip whitespace, and filter out empty strings
            return [tag.strip() for tag in tags.split(',') if tag.strip()]
        return []

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            # Handle tags
            if 'tags' in self.cleaned_data:
                instance.tags.clear()
                for tag_name in self.cleaned_data['tags']:
                    tag, _ = NoteTag.objects.get_or_create(name=tag_name)
                    instance.tags.add(tag)
        return instance

    def get_sections(self):
        return [
            {
                'title': 'Note Details',
                'description': 'Enter the note details',
                'fields': ['title', 'category']
            },
            {
                'title': 'Note Content',
                'description': 'Enter your note',
                'fields': ['content']
            },
            {
                'title': 'Organization',
                'description': 'Organize your note',
                'fields': ['tags', 'is_pinned']
            }
        ]

class NoteAttachmentForm(forms.ModelForm):
    class Meta:
        model = NoteAttachment
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'})
        }

class PatientSearchForm(forms.Form):
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
        """Check if a field was explicitly set by the user"""
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
        """Return a dictionary of filters that are actually in use"""
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

