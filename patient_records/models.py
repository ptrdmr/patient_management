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

    def get_gender_display(self):
        return dict(self.GENDER_CHOICES).get(self.gender, 'None')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        # Generate patient number if it doesn't exist
        if not self.patient_number:
            year = datetime.date.today().year
            # Get the last patient number for this year
            last_patient = Patient.objects.filter(
                patient_number__startswith=str(year)
            ).order_by('-patient_number').first()
            
            if last_patient:
                # Extract the sequence number and increment
                last_seq = int(last_patient.patient_number[-6:])
                new_seq = str(last_seq + 1).zfill(6)
            else:
                # First patient of the year
                new_seq = '000001'
            
            self.patient_number = f'{year}{new_seq}'

        # Handle empty strings for fields
        fields_to_check = ['marital_status', 'street_address', 'city', 'state', 
                          'zip', 'patient_phone', 'patient_email', 'poa_name', 
                          'relationship', 'poa_contact']
        
        for field in fields_to_check:
            value = getattr(self, field)
            if value == '':
                setattr(self, field, None)
                
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Diagnosis(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    icd_code = models.CharField(max_length=10)
    diagnosis = models.CharField(max_length=255)
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "diagnoses"
        ordering = ['-date']

    def __str__(self):
        return f"{self.icd_code} - {self.diagnosis}"

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
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    sodium = models.DecimalField(max_digits=5, decimal_places=2)
    potassium = models.DecimalField(max_digits=5, decimal_places=2)
    chloride = models.DecimalField(max_digits=5, decimal_places=2)
    co2 = models.DecimalField(max_digits=5, decimal_places=2)
    glucose = models.DecimalField(max_digits=5, decimal_places=2)
    bun = models.DecimalField(max_digits=5, decimal_places=2)
    creatinine = models.DecimalField(max_digits=5, decimal_places=2)
    calcium = models.DecimalField(max_digits=5, decimal_places=2)
    protein = models.DecimalField(max_digits=5, decimal_places=2)
    albumin = models.DecimalField(max_digits=5, decimal_places=2)
    bilirubin = models.DecimalField(max_digits=5, decimal_places=2)
    gfr = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"CMP Labs - {self.patient} - {self.date}"

class CbcLabs(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    rbc = models.DecimalField(max_digits=5, decimal_places=2)
    wbc = models.DecimalField(max_digits=5, decimal_places=2)
    hemoglobin = models.DecimalField(max_digits=5, decimal_places=2)
    hematocrit = models.DecimalField(max_digits=5, decimal_places=2)
    mcv = models.DecimalField(max_digits=5, decimal_places=2)
    mchc = models.DecimalField(max_digits=5, decimal_places=2)
    rdw = models.DecimalField(max_digits=5, decimal_places=2)
    platelets = models.DecimalField(max_digits=7, decimal_places=2)
    mch = models.DecimalField(max_digits=5, decimal_places=2)
    neutrophils = models.DecimalField(max_digits=5, decimal_places=2)
    lymphocytes = models.DecimalField(max_digits=5, decimal_places=2)
    monocytes = models.DecimalField(max_digits=5, decimal_places=2)
    eosinophils = models.DecimalField(max_digits=5, decimal_places=2)
    basophils = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"CBC Labs - {self.patient} - {self.date}"

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
    date_prescribed = models.DateField()
    drug = models.CharField(max_length=200)
    dose = models.CharField(max_length=100)
    route = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    prn = models.BooleanField(default=False)
    dc_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['-date_prescribed']),
            models.Index(fields=['patient', '-date_prescribed']),
        ]

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
        ('VIEW', 'View'),
    ]
    
    RECORD_TYPE_CHOICES = [
        ('PATIENT', 'Patient Demographics'),
        ('CLINICAL_NOTE', 'Clinical Notes'),
        ('CBC_LAB', 'CBC Lab Results'),
        ('CMP_LAB', 'CMP Lab Results'),
        ('MEDICATION', 'Medications'),
        ('SYMPTOM', 'Symptoms'),
    ]

    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    record_type = models.CharField(max_length=20, choices=RECORD_TYPE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    previous_values = models.JSONField(default=dict)
    new_values = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True)

    class Meta:
        indexes = [
            models.Index(fields=['patient', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['record_type', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.get_action_display()} {self.get_record_type_display()} by {self.user} on {self.timestamp}"

# Add this model after your existing models
class ClinicalNotes(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    provider = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True)
    notes = models.TextField()
    source = models.CharField(max_length=100, default='manual')
    
    class Meta:
        ordering = ['-date']
        verbose_name = 'Clinical Note'
        verbose_name_plural = 'Clinical Notes'
        indexes = [
            models.Index(fields=['-date']),
            models.Index(fields=['patient', '-date']),
        ]

    def __str__(self):
        return f"Clinical Note - {self.patient} - {self.date}"

