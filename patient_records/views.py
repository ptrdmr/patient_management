from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *
from .forms import *  # We'll create these forms next

def home(request):
    """Home page view"""
    return render(request, 'patient_records/home.html')

def add_patient(request):
    """Add new patient demographics"""
    if request.method == 'POST':
        form = PatientDemographicsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Patient demographics saved successfully!')
            return redirect('patient_list')
    else:
        form = PatientDemographicsForm()
    return render(request, 'patient_records/add_patient.html', {'form': form})

def patient_list(request):
    """View list of all patients"""
    patients = PatientDemographics.objects.all().order_by('-date')
    return render(request, 'patient_records/patient_list.html', {'patients': patients})

def patient_detail(request, patient_id):
    """View detailed patient information"""
    patient = get_object_or_404(PatientDemographics, id=patient_id)
    context = {
        'patient': patient,
        'diagnoses': Diagnosis.objects.filter(patient=patient),
        'visits': Visits.objects.filter(patient=patient),
        'vitals': Vitals.objects.filter(patient=patient),
        'cmp_labs': CmpLabs.objects.filter(patient=patient),
        'cbc_labs': CbcLabs.objects.filter(patient=patient),
        'symptoms': Symptoms.objects.filter(patient=patient),
        'medications': Medications.objects.filter(patient=patient),
        'measurements': Measurements.objects.filter(patient=patient),
        'imaging': Imaging.objects.filter(patient=patient),
        'adls': Adls.objects.filter(patient=patient),
        'occurrences': Occurrences.objects.filter(patient=patient),
    }
    return render(request, 'patient_records/patient_detail.html', context)

def add_diagnosis(request, patient_id):
    """Add diagnosis for a patient"""
    patient = get_object_or_404(PatientDemographics, id=patient_id)
    if request.method == 'POST':
        form = DiagnosisForm(request.POST)
        if form.is_valid():
            diagnosis = form.save(commit=False)
            diagnosis.patient = patient
            diagnosis.save()
            messages.success(request, 'Diagnosis added successfully!')
            return redirect('patient_detail', patient_id=patient_id)
    else:
        form = DiagnosisForm(initial={'patient': patient})
    return render(request, 'patient_records/add_diagnosis.html', {'form': form, 'patient': patient})

def add_vitals(request, patient_id):
    """Add vitals for a patient"""
    patient = get_object_or_404(PatientDemographics, id=patient_id)
    if request.method == 'POST':
        form = VitalsForm(request.POST)
        if form.is_valid():
            vitals = form.save(commit=False)
            vitals.patient = patient
            vitals.save()
            messages.success(request, 'Vitals added successfully!')
            return redirect('patient_detail', patient_id=patient_id)
    else:
        form = VitalsForm(initial={'patient': patient})
    return render(request, 'patient_records/add_vitals.html', {'form': form, 'patient': patient})

def add_labs(request, patient_id):
    """Add lab results for a patient"""
    patient = get_object_or_404(PatientDemographics, id=patient_id)
    if request.method == 'POST':
        cmp_form = CmpLabsForm(request.POST, prefix='cmp')
        cbc_form = CbcLabsForm(request.POST, prefix='cbc')
        if cmp_form.is_valid() and cbc_form.is_valid():
            cmp = cmp_form.save(commit=False)
            cbc = cbc_form.save(commit=False)
            cmp.patient = patient
            cbc.patient = patient
            cmp.save()
            cbc.save()
            messages.success(request, 'Lab results added successfully!')
            return redirect('patient_detail', patient_id=patient_id)
    else:
        cmp_form = CmpLabsForm(prefix='cmp', initial={'patient': patient})
        cbc_form = CbcLabsForm(prefix='cbc', initial={'patient': patient})
    return render(request, 'patient_records/add_labs.html', {
        'cmp_form': cmp_form,
        'cbc_form': cbc_form,
        'patient': patient
    })

def add_medications(request, patient_id):
    """Add medications for a patient"""
    patient = get_object_or_404(PatientDemographics, id=patient_id)
    if request.method == 'POST':
        form = MedicationsForm(request.POST)
        if form.is_valid():
            med = form.save(commit=False)
            med.patient = patient
            med.save()
            messages.success(request, 'Medication added successfully!')
            return redirect('patient_detail', patient_id=patient_id)
    else:
        form = MedicationsForm(initial={'patient': patient})
    return render(request, 'patient_records/add_medications.html', {'form': form, 'patient': patient})

def add_measurements(request, patient_id):
    """Add measurements for a patient"""
    patient = get_object_or_404(PatientDemographics, id=patient_id)
    if request.method == 'POST':
        form = MeasurementsForm(request.POST)
        if form.is_valid():
            measurement = form.save(commit=False)
            measurement.patient = patient
            measurement.save()
            messages.success(request, 'Measurements added successfully!')
            return redirect('patient_detail', patient_id=patient_id)
    else:
        form = MeasurementsForm(initial={'patient': patient})
    return render(request, 'patient_records/add_measurements.html', {'form': form, 'patient': patient})

def add_adls(request, patient_id):
    """Add ADLs for a patient"""
    patient = get_object_or_404(PatientDemographics, id=patient_id)
    if request.method == 'POST':
        form = AdlsForm(request.POST)
        if form.is_valid():
            adls = form.save(commit=False)
            adls.patient = patient
            adls.save()
            messages.success(request, 'ADLs added successfully!')
            return redirect('patient_detail', patient_id=patient_id)
    else:
        form = AdlsForm(initial={'patient': patient})
    return render(request, 'patient_records/add_adls.html', {'form': form, 'patient': patient})

def add_symptoms(request, patient_id):
    """Add symptoms for a patient"""
    patient = get_object_or_404(PatientDemographics, id=patient_id)
    if request.method == 'POST':
        form = SymptomsForm(request.POST)
        if form.is_valid():
            symptom = form.save(commit=False)
            symptom.patient = patient
            symptom.save()
            messages.success(request, 'Symptoms added successfully!')
            return redirect('patient_detail', patient_id=patient_id)
    else:
        form = SymptomsForm(initial={'patient': patient})
    return render(request, 'patient_records/add_symptoms.html', {'form': form, 'patient': patient})

def add_occurrence(request, patient_id):
    """Add occurrence for a patient"""
    patient = get_object_or_404(PatientDemographics, id=patient_id)
    if request.method == 'POST':
        form = OccurrencesForm(request.POST)
        if form.is_valid():
            occurrence = form.save(commit=False)
            occurrence.patient = patient
            occurrence.save()
            messages.success(request, 'Occurrence added successfully!')
            return redirect('patient_detail', patient_id=patient_id)
    else:
        form = OccurrencesForm(initial={'patient': patient})
    return render(request, 'patient_records/add_occurrence.html', {'form': form, 'patient': patient})

def add_imaging(request, patient_id):
    """Add imaging for a patient"""
    patient = get_object_or_404(PatientDemographics, id=patient_id)
    if request.method == 'POST':
        form = ImagingForm(request.POST)
        if form.is_valid():
            imaging = form.save(commit=False)
            imaging.patient = patient
            imaging.save()
            messages.success(request, 'Imaging added successfully!')
            return redirect('patient_detail', patient_id=patient_id)
    else:
        form = ImagingForm(initial={'patient': patient})
    return render(request, 'patient_records/add_imaging.html', {'form': form, 'patient': patient})

def add_provider(request):
    """Add new provider"""
    if request.method == 'POST':
        form = ProviderForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Provider added successfully!')
            return redirect('provider_list')
    else:
        form = ProviderForm()
    return render(request, 'patient_records/add_provider.html', {'form': form})

def provider_list(request):
    """View list of all providers"""
    providers = Provider.objects.all().order_by('provider')
    return render(request, 'patient_records/provider_list.html', {'providers': providers})

def add_record_request(request, patient_id):
    """Add record request for a patient"""
    patient = get_object_or_404(PatientDemographics, id=patient_id)
    if request.method == 'POST':
        form = RecordRequestLogForm(request.POST)
        if form.is_valid():
            record_request = form.save(commit=False)
            record_request.patient = patient
            record_request.save()
            messages.success(request, 'Record request logged successfully!')
            return redirect('patient_detail', patient_id=patient_id)
    else:
        form = RecordRequestLogForm(initial={'patient': patient})
    return render(request, 'patient_records/add_record_request.html', {'form': form, 'patient': patient})