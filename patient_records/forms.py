from django import forms
from .models import *
import datetime
from .widgets import ICDCodeWidget, PhoneNumberWidget

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
        fields = ['provider', 'practice', 'address', 'city', 'state', 'zip', 'fax', 'phone', 'source']

    def get_sections(self):
        return [
            {
                'title': 'Provider Information',
                'fields': ['provider', 'practice']
            },
            {
                'title': 'Contact Information',
                'fields': ['address', 'city', 'state', 'zip', 'phone', 'fax']
            },
            {
                'title': 'Additional Information',
                'fields': ['source']
            }
        ]

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.date:
            instance.date = datetime.date.today()
        if commit:
            instance.save()
        return instance

class DiagnosisForm(forms.ModelForm):
    class Meta:
        model = Diagnosis
        fields = ['icd_code', 'diagnosis', 'date', 'notes']
        widgets = {
            'icd_code': ICDCodeWidget(attrs={
                'placeholder': 'Enter ICD code',
                'data-diagnosis-field': 'diagnosis'
            }),
        }

    def get_sections(self):
        return [
            {
                'title': 'Diagnosis Information',
                'description': 'Enter diagnosis details',
                'fields': ['icd_code', 'diagnosis', 'date', 'notes']
            }
        ]

class VisitsForm(SectionedForm):
    class Meta:
        model = Visits
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

    def get_sections(self):
        return [
            {
                'title': 'Visit Information',
                'description': 'Basic visit details',
                'fields': ['date', 'provider', 'visit_type']
            },
            {
                'title': 'Visit Details',
                'description': 'Notes and observations',
                'fields': ['notes', 'follow_up_needed', 'follow_up_date']
            }
        ]

class VitalsForm(SectionedForm):
    class Meta:
        model = Vitals
        fields = ['date', 'blood_pressure', 'temperature', 'spo2', 'pulse', 
                 'respirations', 'supp_o2', 'pain', 'source']

    def get_sections(self):
        return [
            {
                'title': 'Basic Vitals',
                'description': 'Primary vital signs',
                'fields': ['date', 'blood_pressure', 'temperature', 'pulse']
            },
            {
                'title': 'Respiratory',
                'description': 'Breathing and oxygen levels',
                'fields': ['respirations', 'spo2', 'supp_o2']
            },
            {
                'title': 'Assessment',
                'description': 'Additional measurements',
                'fields': ['pain', 'source']
            }
        ]

class CmpLabsForm(SectionedForm):
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date'},
            format='%Y-%m-%d'
        )
    )

    class Meta:
        model = CmpLabs
        fields = ['date', 'sodium', 'potassium', 'chloride', 'co2', 
                 'glucose', 'bun', 'creatinine', 'calcium',
                 'protein', 'albumin', 'bilirubin', 'gfr']

    def get_sections(self):
        return [
            {
                'title': 'Basic Information',
                'description': 'Date of lab results',
                'fields': ['date']
            },
            {
                'title': 'Electrolytes',
                'description': 'Electrolyte measurements',
                'fields': ['sodium', 'potassium', 'chloride', 'co2']
            },
            {
                'title': 'Metabolic Panel',
                'description': 'Basic metabolic measurements',
                'fields': ['glucose', 'bun', 'creatinine', 'calcium']
            },
            {
                'title': 'Liver Function',
                'description': 'Liver function tests',
                'fields': ['protein', 'albumin', 'bilirubin', 'gfr']
            }
        ]

class CbcLabsForm(SectionedForm):
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date'},
            format='%Y-%m-%d'
        )
    )

    class Meta:
        model = CbcLabs
        fields = ['date', 'rbc', 'wbc', 'hemoglobin', 'hematocrit', 'mcv', 
                 'mchc', 'rdw', 'platelets', 'mch', 'neutrophils', 
                 'lymphocytes', 'monocytes', 'eosinophils', 'basophils']

    def get_sections(self):
        return [
            {
                'title': 'Basic Information',
                'description': 'Date of lab results',
                'fields': ['date']
            },
            {
                'title': 'Red Blood Cell Counts',
                'description': 'RBC-related measurements',
                'fields': ['rbc', 'hemoglobin', 'hematocrit']
            },
            {
                'title': 'White Blood Cell Counts',
                'description': 'WBC-related measurements',
                'fields': ['wbc', 'neutrophils', 'lymphocytes', 'monocytes', 
                          'eosinophils', 'basophils']
            },
            {
                'title': 'Cell Indices',
                'description': 'Blood cell characteristics',
                'fields': ['mcv', 'mchc', 'rdw', 'mch']
            },
            {
                'title': 'Platelets',
                'description': 'Platelet count',
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

class ImagingForm(SectionedForm):
    class Meta:
        model = Imaging
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

    def get_sections(self):
        return [
            {
                'title': 'Study Information',
                'description': 'Basic imaging details',
                'fields': ['date', 'study_type', 'body_area']
            },
            {
                'title': 'Results',
                'description': 'Findings and interpretation',
                'fields': ['findings', 'impression', 'notes']
            },
            {
                'title': 'Additional Information',
                'description': 'Source and follow-up',
                'fields': ['source', 'follow_up_needed']
            }
        ]

class AdlsForm(SectionedForm):
    class Meta:
        model = Adls
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

    def get_sections(self):
        return [
            {
                'title': 'Basic Information',
                'description': 'Assessment date and type',
                'fields': ['date', 'assessment_type']
            },
            {
                'title': 'Daily Living Activities',
                'description': 'Basic ADL scores',
                'fields': ['bathing', 'dressing', 'toileting', 'transferring', 'continence', 'feeding']
            },
            {
                'title': 'Additional Information',
                'description': 'Notes and observations',
                'fields': ['notes', 'source']
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
        fields = '__all__'
        widgets = {
            'date_requested': forms.DateInput(attrs={'type': 'date'}),
            'date_sent': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

    def get_sections(self):
        return [
            {
                'title': 'Request Information',
                'description': 'Basic request details',
                'fields': ['date_requested', 'requestor', 'request_type', 'urgency']
            },
            {
                'title': 'Record Details',
                'description': 'What records were requested',
                'fields': ['records_requested', 'date_range_start', 'date_range_end']
            },
            {
                'title': 'Processing Information',
                'description': 'Status and delivery details',
                'fields': ['status', 'date_sent', 'delivery_method', 'notes']
            }
        ]

class PatientForm(SectionedForm):
    class Meta:
        model = Patient
        fields = [
            # Basic Information
            'first_name', 'middle_name', 'last_name', 'date_of_birth', 
            'gender', 'ssn', 'marital_status',
            
            # Contact Information
            'street_address', 'city', 'state', 'zip',
            'patient_phone', 'patient_email',
            
            # Power of Attorney
            'poa_name', 'relationship', 'poa_contact',
            
            # Medical Information
            'allergies', 'code_status'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'max': datetime.date.today().isoformat()
                }
            ),
        }

    def get_sections(self):
        return [
            {
                'title': 'Basic Information',
                'fields': ['first_name', 'middle_name', 'last_name', 
                          'date_of_birth', 'gender', 'ssn', 'marital_status']
            },
            {
                'title': 'Contact Information',
                'fields': ['street_address', 'city', 'state', 'zip',
                          'patient_phone', 'patient_email']
            },
            {
                'title': 'Power of Attorney',
                'fields': ['poa_name', 'relationship', 'poa_contact']
            },
            {
                'title': 'Medical Information',
                'fields': ['allergies', 'code_status']
            }
        ]

