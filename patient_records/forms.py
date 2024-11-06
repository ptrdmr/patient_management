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
            'street_address', 'city', 'state', 'zip', 'patient_phone', 'patient_email'
        ]