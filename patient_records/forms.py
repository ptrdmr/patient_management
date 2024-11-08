from django import forms
from .models import *
import datetime



class ProviderForm(forms.ModelForm):
    class Meta:
        model = Provider
        fields = [
            'provider', 'practice', 'address', 'city', 
            'state', 'zip', 'fax', 'phone', 'source'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Define form sections
        self.sections = [
            {
                'title': 'Provider Information',
                'description': 'Basic provider details',
                'fields': ['provider', 'practice']
            },
            {
                'title': 'Contact Details',
                'description': 'Address and contact information',
                'fields': ['address', 'city', 'state', 'zip', 'phone', 'fax']
            },
            {
                'title': 'Additional Information',
                'description': 'Other relevant details',
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
        fields = ['date', 'diagnosis', 'icd_code', 'source']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sections = [
            {
                'title': 'Diagnosis Details',
                'description': 'Primary diagnosis information',
                'fields': ['date', 'diagnosis', 'icd_code']
            },
            {
                'title': 'Additional Information',
                'description': 'Source and other details',
                'fields': ['source']
            }
        ]

class VisitsForm(forms.ModelForm):
    class Meta:
        model = Visits
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

class VitalsForm(forms.ModelForm):
    class Meta:
        model = Vitals
        fields = ['date', 'blood_pressure', 'temperature', 'spo2', 'pulse', 
                 'respirations', 'supp_o2', 'pain', 'source']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sections = [
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

class CmpLabsForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date'},
            format='%Y-%m-%d'
        )
    )

    class Meta:
        model = CmpLabs
        fields = ['date', 'bun', 'sodium', 'protein', 'albumin', 'bilirubin', 
                 'gfr', 'potassium', 'chloride', 'co2', 'glucose', 'creatinine']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sections = [
            {
                'title': 'Basic Information',
                'description': 'Date of lab results',
                'fields': ['date']
            },
            {
                'title': 'Metabolic Panel',
                'description': 'Primary metabolic indicators',
                'fields': ['bun', 'sodium', 'protein', 'albumin']
            },
            {
                'title': 'Liver Function',
                'description': 'Liver-related measurements',
                'fields': ['bilirubin', 'gfr']
            },
            {
                'title': 'Electrolytes',
                'description': 'Electrolyte measurements',
                'fields': ['potassium', 'chloride', 'co2']
            },
            {
                'title': 'Additional Tests',
                'description': 'Other metabolic indicators',
                'fields': ['glucose', 'creatinine']
            }
        ]

class CbcLabsForm(forms.ModelForm):
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sections = [
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

class SymptomsForm(forms.ModelForm):
    class Meta:
        model = Symptoms
        fields = ['date', 'symptom', 'notes', 'source', 'person_reporting']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sections = [
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

class MedicationsForm(forms.ModelForm):
    class Meta:
        model = Medications
        fields = ['date', 'drug', 'dose', 'route', 'frequency', 'prn', 'dc_date', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sections = [
            {
                'title': 'Medication Details',
                'description': 'Basic medication information',
                'fields': ['date', 'drug', 'dose']
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

class MeasurementsForm(forms.ModelForm):
    class Meta:
        model = Measurements
        fields = ['date', 'weight', 'nutritional_intake', 'mac', 'fast', 'pps', 'plof', 'source']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sections = [
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

class ImagingForm(forms.ModelForm):
    class Meta:
        model = Imaging
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

class AdlsForm(forms.ModelForm):
    class Meta:
        model = Adls
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

class OccurrencesForm(forms.ModelForm):
    class Meta:
        model = Occurrences
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

class RecordRequestLogForm(forms.ModelForm):
    class Meta:
        model = RecordRequestLog
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'received_on': forms.DateInput(attrs={'type': 'date'}),
            'processed_date': forms.DateInput(attrs={'type': 'date'}),
        }

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'first_name', 'middle_name', 'last_name', 'date_of_birth', 
            'gender', 'ssn', 'allergies', 'code_status', 'height_cm', 'height_inches',
            'poa_name', 'relationship', 'poa_contact',
            'veteran', 'veteran_spouse', 'marital_status',
            'street_address', 'city', 'state', 'zip', 'patient_phone', 'patient_email'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'ssn': forms.TextInput(attrs={'pattern': r'\d{3}-\d{2}-\d{4}', 'placeholder': 'XXX-XX-XXXX'}),
            'height_cm': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'height_inches': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sections = [
            {
                'title': 'Basic Information',
                'description': 'Primary patient identification',
                'fields': ['first_name', 'middle_name', 'last_name', 'date_of_birth', 'gender', 'ssn']
            },
            {
                'title': 'Medical Information',
                'description': 'Health-related details',
                'fields': ['allergies', 'code_status', 'height_cm', 'height_inches']
            },
            {
                'title': 'Power of Attorney',
                'description': 'POA contact information',
                'fields': ['poa_name', 'relationship', 'poa_contact']
            },
            {
                'title': 'Status Information',
                'description': 'Additional patient status details',
                'fields': ['veteran', 'veteran_spouse', 'marital_status']
            },
            {
                'title': 'Contact Information',
                'description': 'Patient contact details',
                'fields': ['street_address', 'city', 'state', 'zip', 'patient_phone', 'patient_email']
            }
        ]

    def clean_ssn(self):
        ssn = self.cleaned_data['ssn']
        # Remove any existing hyphens and add them back in correct positions
        ssn = ''.join(c for c in ssn if c.isdigit())
        if len(ssn) != 9:
            raise forms.ValidationError("SSN must be 9 digits")
        return f"{ssn[:3]}-{ssn[3:5]}-{ssn[5:]}"