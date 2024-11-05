from django import forms
from .models import PatientDemographics, Diagnosis

class PatientDemographicsForm(forms.ModelForm):
    class Meta:
        model = PatientDemographics
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'veteran': forms.CheckboxInput(),
            'veteran_spouse': forms.CheckboxInput(),
        }

class DiagnosisForm(forms.ModelForm):
    class Meta:
        model = Diagnosis
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }