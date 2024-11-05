from django.db import models

class PatientDemographics(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    date = models.DateField()
    allergies = models.TextField(blank=True)
    code_status = models.CharField(max_length=100)
    poa_name = models.CharField(max_length=200)
    relationship = models.CharField(max_length=100)
    poa_contact = models.CharField(max_length=100)
    veteran = models.BooleanField(default=False)
    veteran_spouse = models.BooleanField(default=False)
    marital_status = models.CharField(max_length=50)
    street_address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=10)
    patient_phone = models.CharField(max_length=20)
    patient_email = models.EmailField()

class Diagnosis(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    patient = models.ForeignKey(PatientDemographics, on_delete=models.CASCADE)
    date = models.DateField()
    diagnosis = models.CharField(max_length=200)
    icd_code = models.CharField(max_length=20)
    source = models.CharField(max_length=100)
