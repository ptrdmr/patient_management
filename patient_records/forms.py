from django import forms
from .models import *



class ProviderForm(forms.ModelForm):
    class Meta:
        model = Provider
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class DiagnosisForm(forms.ModelForm):
    class Meta:
        model = Diagnosis
        fields = ['date', 'diagnosis', 'icd_code', 'source']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

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
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'supp_o2': forms.CheckboxInput(),
        }

class CmpLabsForm(forms.ModelForm):
    class Meta:
        model = CmpLabs
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class CbcLabsForm(forms.ModelForm):
    class Meta:
        model = CbcLabs
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class SymptomsForm(forms.ModelForm):
    class Meta:
        model = Symptoms
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

class MedicationsForm(forms.ModelForm):
    class Meta:
        model = Medications
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'dc_date': forms.DateInput(attrs={'type': 'date'}),
            'prn': forms.CheckboxInput(),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

class MeasurementsForm(forms.ModelForm):
    class Meta:
        model = Measurements
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

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
            'date', 'allergies', 'code_status', 'poa_name', 'relationship', 
            'poa_contact', 'veteran', 'veteran_spouse', 'marital_status', 
            'street_address', 'city', 'state', 'zip', 'patient_phone', 'patient_email',
            'first_name', 'middle_name', 'last_name', 'date_of_birth', 
            'gender', 'ssn', 'height_cm', 'height_inches'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'ssn': forms.TextInput(attrs={'pattern': r'\d{3}-\d{2}-\d{4}', 'placeholder': 'XXX-XX-XXXX'}),
            'height_cm': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'height_inches': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

    def clean_ssn(self):
        ssn = self.cleaned_data['ssn']
        # Remove any existing hyphens and add them back in correct positions
        ssn = ''.join(c for c in ssn if c.isdigit())
        if len(ssn) != 9:
            raise forms.ValidationError("SSN must be 9 digits")
        return f"{ssn[:3]}-{ssn[3:5]}-{ssn[5:]}"