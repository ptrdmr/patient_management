# Medication Tracking

## Overview
The Medication Tracking module manages patient medications, prescriptions, and medication administration records (MAR).

## Features

### Medication Management
```python
class Medication(models.Model):
    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200)
    drug_class = models.CharField(max_length=100)
    strength = models.CharField(max_length=50)
    unit = models.CharField(max_length=20)
    form = models.CharField(max_length=50)  # tablet, capsule, liquid
    manufacturer = models.CharField(max_length=100)
    ndc_code = models.CharField(max_length=11, unique=True)
```

### Prescription Management
```python
class Prescription(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    medication = models.ForeignKey('Medication', on_delete=models.PROTECT)
    prescriber = models.ForeignKey('Provider', on_delete=models.PROTECT)
    dosage = models.CharField(max_length=50)
    frequency = models.CharField(max_length=50)
    route = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    instructions = models.TextField()
    active = models.BooleanField(default=True)
```

## Medication Administration

### MAR Entry
```python
class MedicationAdministration(models.Model):
    prescription = models.ForeignKey('Prescription', on_delete=models.PROTECT)
    administered_by = models.ForeignKey('Staff', on_delete=models.PROTECT)
    administered_at = models.DateTimeField()
    dose_given = models.CharField(max_length=50)
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('GIVEN', 'Administered'),
            ('REFUSED', 'Patient Refused'),
            ('HELD', 'Medication Held'),
            ('MISSED', 'Dose Missed')
        ]
    )
```

## Medication Safety

### Drug Interaction Checking
```python
def check_drug_interactions(patient_id, new_medication_id):
    """Check for potential drug interactions."""
    current_medications = Prescription.objects.filter(
        patient_id=patient_id,
        active=True
    ).select_related('medication')
    
    new_medication = Medication.objects.get(id=new_medication_id)
    
    interactions = DrugInteraction.objects.filter(
        Q(drug_a=new_medication) |
        Q(drug_b=new_medication)
    )
    
    return [
        interaction for interaction in interactions
        if interaction.drug_a in current_medications or
           interaction.drug_b in current_medications
    ]
```

### Allergy Verification
```python
def verify_medication_allergies(patient_id, medication_id):
    """Verify medication against patient allergies."""
    patient = Patient.objects.get(id=patient_id)
    medication = Medication.objects.get(id=medication_id)
    
    allergies = patient.allergies.all()
    
    return any(
        allergy.substance.lower() in medication.name.lower() or
        allergy.substance.lower() in medication.generic_name.lower()
        for allergy in allergies
    )
```

## Reporting

### Medication History Report
```python
def generate_medication_history(patient_id, start_date=None, end_date=None):
    """Generate medication history report."""
    prescriptions = Prescription.objects.filter(
        patient_id=patient_id,
        start_date__gte=start_date if start_date else '-infinity',
        start_date__lte=end_date if end_date else 'infinity'
    ).select_related(
        'medication',
        'prescriber'
    ).prefetch_related(
        'medicationadministration_set'
    )
    
    return {
        'prescriptions': prescriptions,
        'total_medications': prescriptions.count(),
        'active_medications': prescriptions.filter(active=True).count()
    }
```

## Integration

### E-Prescribing
```python
class EPrescription(models.Model):
    prescription = models.OneToOneField('Prescription', on_delete=models.CASCADE)
    external_id = models.CharField(max_length=100, unique=True)
    pharmacy = models.ForeignKey('Pharmacy', on_delete=models.PROTECT)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('SENT', 'Sent to Pharmacy'),
            ('FILLED', 'Filled'),
            ('CANCELLED', 'Cancelled')
        ]
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    filled_at = models.DateTimeField(null=True)
```

## Related Documentation
- [[Patient Records & Demographics]]
- [[Clinical Information Management]]
- [[API Reference]]
- [[Security Implementation]]

## Tags
#medications #prescriptions #mar #drug-safety 