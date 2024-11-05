from django.shortcuts import render, redirect
from .forms import PatientDemographicsForm
from django.contrib import messages

def add_patient(request):
    if request.method == 'POST':
        form = PatientDemographicsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Patient information saved successfully!')
            return redirect('add_patient')
    else:
        form = PatientDemographicsForm()
    return render(request, 'patient_records/add_patient.html', {'form': form})