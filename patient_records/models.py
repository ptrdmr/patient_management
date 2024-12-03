from django.db import models
from django.contrib.auth.models import User
import datetime
import uuid
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

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
    provider = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True)
    source = models.CharField(max_length=100, blank=True, null=True)
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
    chief_complaint = models.TextField(blank=True, null=True)
    assessment = models.TextField(blank=True, null=True)
    plan = models.TextField(blank=True, null=True)
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
    severity = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    source = models.CharField(max_length=100)
    person_reporting = models.CharField(max_length=200)

class Medications(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date_prescribed = models.DateField()
    drug = models.CharField(max_length=200)
    dose = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    route = models.CharField(max_length=100)
    notes = models.TextField(blank=True, null=True)
    # Add the new fields
    prn = models.BooleanField(default=False, verbose_name="PRN (As Needed)")
    dc_date = models.DateField(null=True, blank=True, verbose_name="Discontinue Date")

    class Meta:
        indexes = [
            models.Index(fields=['-date_prescribed']),
            models.Index(fields=['patient', '-date_prescribed']),
        ]

    def __str__(self):
        return f"{self.drug} - {self.dose}"

class Measurements(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    weight = models.FloatField()
    value = models.FloatField(null=True, blank=True)
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
    body_part = models.CharField(max_length=100, blank=True, null=True)
    findings = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True)
    source = models.CharField(max_length=100)

class Adls(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    ambulation = models.CharField(max_length=100)
    continence = models.CharField(max_length=100)
    transfer = models.CharField(max_length=100)
    toileting = models.CharField(max_length=100, blank=True, null=True)
    transferring = models.CharField(max_length=100, blank=True, null=True)
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
    action_taken = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True)
    source = models.CharField(max_length=100)

class RecordRequestLog(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    request_type = models.CharField(max_length=100, blank=True, null=True)
    purpose = models.TextField(blank=True, null=True)
    records_requested = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=100, blank=True, null=True)

class AuditTrail(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.SET_NULL, null=True)
    patient_identifier = models.CharField(max_length=100, default="Unknown Patient")
    action = models.CharField(
        max_length=10,
        choices=[('CREATE', 'Create'), ('UPDATE', 'Update'), ('DELETE', 'Delete')]
    )
    record_type = models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    previous_values = models.JSONField(default=dict)
    new_values = models.JSONField(default=dict)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['patient_identifier', '-timestamp']),
            models.Index(fields=['action', '-timestamp'])
        ]

    def __str__(self):
        return f"{self.action} {self.record_type} - {self.patient_identifier or 'Unknown'}"

    def save(self, *args, **kwargs):
        # Ensure patient_identifier is set even if patient is null
        if not self.patient_identifier and self.patient:
            self.patient_identifier = f"{self.patient.patient_number} - {self.patient.first_name} {self.patient.last_name}"
        super().save(*args, **kwargs)

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

class NoteTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class PatientNote(models.Model):
    NOTE_CATEGORIES = [
        ('OVERVIEW', 'Overview'),
        ('CLINICAL', 'Clinical Data'),
        ('VISITS', 'Visits'),
        ('MEDICATIONS', 'Medications'),
        ('LABS', 'Lab Results'),
        ('VITALS', 'Vital Signs'),
        ('GENERAL', 'General Notes'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=NOTE_CATEGORIES, default='GENERAL')
    tags = models.ManyToManyField(NoteTag, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_pinned = models.BooleanField(default=False)
    
    # Reference to any patient record
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.CharField(max_length=100, null=True, blank=True)
    referenced_record = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-is_pinned', '-created_at']
        indexes = [
            models.Index(fields=['patient', '-created_at']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.title} - {self.patient}"

    @property
    def short_content(self):
        """Return truncated content for preview"""
        return self.content[:150] + '...' if len(self.content) > 150 else self.content

class NoteAttachment(models.Model):
    note = models.ForeignKey(PatientNote, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='note_attachments/%Y/%m/%d/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_type = models.CharField(max_length=50)

    def __str__(self):
        return self.filename

    def save(self, *args, **kwargs):
        if not self.filename:
            self.filename = self.file.name
        super().save(*args, **kwargs)

