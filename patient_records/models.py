from django.db import models
from django.contrib.auth.models import User
import datetime

class Provider(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    provider = models.CharField(max_length=100)
    practice = models.CharField(max_length=200)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip = models.CharField(max_length=20)
    fax = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    source = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.provider

class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    id = models.AutoField(primary_key=True)
    date = models.DateField()
    allergies = models.TextField(blank=True, null=True)
    code_status = models.CharField(max_length=50, blank=True, null=True)
    poa_name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50, blank=True, null=True)
    poa_contact = models.CharField(max_length=100)
    veteran = models.BooleanField(default=False)
    veteran_spouse = models.BooleanField(default=False)
    marital_status = models.CharField(max_length=50, blank=True, null=True)
    street_address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip = models.CharField(max_length=20, blank=True, null=True)
    patient_phone = models.CharField(max_length=20, blank=True, null=True)
    patient_email = models.EmailField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    patient_number = models.CharField(max_length=10, unique=True, editable=False, null=True, blank=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    ssn = models.CharField(max_length=11, verbose_name="SSN", null=True, blank=True)
    height_cm = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Height (cm)", null=True, blank=True)
    height_inches = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Height (inches)", null=True, blank=True)

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.last_name}, {self.first_name} ({self.patient_number})"
        return f"Patient {self.patient_number}"

    def save(self, *args, **kwargs):
        # Generate patient number if not exists
        if not self.patient_number:
            year = datetime.datetime.now().year
            last_patient = Patient.objects.filter(
                patient_number__startswith=f"{year}"
            ).order_by('-patient_number').first()
            
            if last_patient:
                last_number = int(last_patient.patient_number[4:])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.patient_number = f"{year}{new_number:06d}"
        
        # Height conversion logic - updated to handle Decimal types
        if self.height_cm and not self.height_inches:
            self.height_inches = float(self.height_cm) / 2.54
        elif self.height_inches and not self.height_cm:
            self.height_cm = float(self.height_inches) * 2.54
        
        super().save(*args, **kwargs)

class Diagnosis(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    diagnosis = models.CharField(max_length=200)
    icd_code = models.CharField(max_length=20)
    source = models.CharField(max_length=100)

class Visits(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    visit_type = models.CharField(max_length=100)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    practice = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    source = models.CharField(max_length=100)

class Vitals(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    blood_pressure = models.CharField(max_length=20)
    temperature = models.FloatField()
    spo2 = models.FloatField()
    pulse = models.IntegerField()
    respirations = models.IntegerField()
    supp_o2 = models.BooleanField(default=False)
    pain = models.IntegerField()
    source = models.CharField(max_length=100)

class CmpLabs(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    bun = models.FloatField()
    globulin = models.FloatField()
    ag_ratio = models.FloatField()
    alk_phos = models.FloatField()
    ast = models.FloatField()
    alt = models.FloatField()
    sodium = models.FloatField()
    calcium = models.FloatField()
    protein = models.FloatField()
    albumin = models.FloatField()
    bilirubin = models.FloatField()
    gfr = models.FloatField()
    potassium = models.FloatField()
    chloride = models.FloatField()
    co2 = models.FloatField()
    glucose = models.FloatField()
    creatinine = models.FloatField()

class CbcLabs(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    rbc = models.FloatField()
    wbc = models.FloatField()
    hemoglobin = models.FloatField()
    hematocrit = models.FloatField()
    mcv = models.FloatField()
    mchc = models.FloatField()
    rdw = models.FloatField()
    platelets = models.IntegerField()
    mch = models.FloatField()
    erythrocyte_mcv = models.FloatField()
    neutrophils = models.FloatField()
    lymphocytes = models.FloatField()
    monocytes = models.FloatField()
    eosinophils = models.FloatField()
    basophils = models.FloatField()

class Symptoms(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    symptom = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    source = models.CharField(max_length=100)
    person_reporting = models.CharField(max_length=200)

class Medications(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    drug = models.CharField(max_length=200)
    dose = models.CharField(max_length=100)
    route = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    prn = models.BooleanField(default=False)
    dc_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

class Measurements(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    weight = models.FloatField()
    source = models.CharField(max_length=100)
    nutritional_intake = models.CharField(max_length=200)
    mac = models.CharField(max_length=100)
    fast = models.CharField(max_length=100)
    pps = models.CharField(max_length=100)
    plof = models.CharField(max_length=100)

class Imaging(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    type = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    source = models.CharField(max_length=100)

class Adls(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    ambulation = models.CharField(max_length=100)
    continence = models.CharField(max_length=100)
    transfer = models.CharField(max_length=100)
    dressing = models.CharField(max_length=100)
    feeding = models.CharField(max_length=100)
    bathing = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    source = models.CharField(max_length=100)

class Occurrences(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    occurrence_type = models.CharField(max_length=100)
    description = models.TextField()
    notes = models.TextField(blank=True)
    source = models.CharField(max_length=100)

class RecordRequestLog(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    document_name = models.CharField(max_length=200)
    requested_from = models.CharField(max_length=200)
    requested_via = models.CharField(max_length=100)
    received_on = models.DateField(null=True, blank=True)
    processed_date = models.DateField(null=True, blank=True)
    processed_by = models.CharField(max_length=200)
    status = models.CharField(max_length=100)

class AuditTrail(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
    ]

    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    changes = models.JSONField(default=dict)  # Provide a default empty dictionary

    def __str__(self):
        return f"{self.action} by {self.user} on {self.timestamp}"