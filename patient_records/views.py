from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.urls import reverse
from .models import *
from .forms import *  # We'll create these forms next
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.http import JsonResponse
import csv
from pathlib import Path
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import user_passes_test
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
import logging
from django.core.paginator import PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.db import connection
import datetime
from django.forms import model_to_dict
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.db import transaction
import decimal
from django.db.models import Model
from typing import Optional, Dict, Any

# Initialize the logger for this module
logger = logging.getLogger('patient_records')  # Note: use the specific logger name we defined in settings.py

def serialize_model_data(record_dict: Dict) -> Dict:
    """Helper function to serialize model data for JSON storage"""
    serialized = {}
    for key, value in record_dict.items():
        if isinstance(value, (datetime.date, datetime.datetime)):
            serialized[key] = value.isoformat()
        elif isinstance(value, decimal.Decimal):
            serialized[key] = float(value)
        elif isinstance(value, Model):  # Handle foreign keys
            serialized[key] = str(value.pk)
        else:
            serialized[key] = value
    return serialized

def create_audit_trail(
    record: Model,
    action: str,
    user: User,
    previous_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None
) -> AuditTrail:
    """
    Create an audit trail entry with enhanced logging
    
    # VICTORY_TAG_20231118: This function successfully handles:
    # - All data types including dates and decimals
    # - Patient vs non-patient records
    # - Full audit trail creation
    # - Proper error logging
    # DO NOT REMOVE - Critical implementation notes
    """
    try:
        model_name = record.__class__.__name__.upper()
        logger.info(f"Creating audit trail - Action: {action}, Model: {model_name}, Record ID: {record.id}")
        
        # Determine identifier
        if hasattr(record, 'patient'):
            identifier = f"{record.patient.patient_number} - {record.patient.first_name} {record.patient.last_name}"
        elif isinstance(record, Patient):
            identifier = f"{record.patient_number} - {record.first_name} {record.last_name}"
        elif isinstance(record, Provider):
            identifier = f"Provider: {record.provider}"
        else:
            identifier = "N/A"
            
        logger.debug(f"Audit identifier: {identifier}")

        # Serialize the values before storage
        previous_values = serialize_model_data(previous_values) if previous_values else {}
        new_values = serialize_model_data(new_values) if new_values else {}

        # Create audit trail
        audit = AuditTrail.objects.create(
            patient=None if isinstance(record, Patient) else getattr(record, 'patient', None),
            patient_identifier=identifier,
            action=action,
            record_type=model_name,
            user=user,
            previous_values=previous_values,
            new_values=new_values
        )
        
        logger.info(f"Successfully created audit trail entry: {audit.id}")
        return audit
        
    except Exception as e:
        logger.error(f"Error creating audit trail: {str(e)}", exc_info=True)
        raise

@login_required
def home(request):
    """Home page view"""
    context = {
        'breadcrumbs': [{'label': 'Home', 'url': None}],
        'page_title': 'Home'
    }
    return render(request, 'patient_records/home.html', context)

@login_required
def add_patient(request):
    """Add new patient demographics"""
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)  # Don't save to DB yet
            patient.date = datetime.date.today()  # Set the date field
            patient.save()  # Now save to DB
            
            AuditTrail.objects.create(
                patient=patient, 
                action='CREATE', 
                user=request.user
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Patient added successfully!',
                    'redirect_url': reverse('patient_detail', args=[patient.id])
                })
            
            messages.success(request, 'Patient added successfully!')
            return redirect('patient_detail', patient_id=patient.id)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    else:
        form = PatientForm()
    
    context = {
        'form': form,
        'breadcrumbs': [
            {'label': 'Patients', 'url': reverse('patient_list')},
            {'label': 'Add Patient', 'url': None}
        ],
        'form_title': 'Add New Patient',
        'submit_label': 'Save Patient',
        'cancel_url': reverse('patient_list'),
    }
    return render(request, 'patient_records/add_patient.html', context)

@login_required
def patient_list(request):
    """View list of all patients"""
    breadcrumbs = [
        {'label': 'Patients', 'url': None}
    ]
    
    search_query = request.GET.get('search', '')
    sort_option = request.GET.get('sort', 'date')
    page_number = request.GET.get('page')

    patients = Patient.objects.all()

    if search_query:
        patients = patients.filter(poa_name__icontains=search_query) | patients.filter(id__icontains=search_query)

    if sort_option:
        patients = patients.order_by(sort_option)

    paginator = Paginator(patients, 10)
    page_obj = paginator.get_page(page_number)

    context = {
        'patients': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': page_obj,
        'search_query': search_query,
        'sort_option': sort_option,
        'breadcrumbs': breadcrumbs,
        'page_title': 'Patient List'
    }
    return render(request, 'patient_records/patient_list.html', context)

@login_required
def patient_detail(request, patient_id):
    try:
        # Get patient with all fields
        patient = Patient.objects.get(id=patient_id)
        
        # Create context with processed data
        context = {
            'patient': patient,
            'recent_medications': Medications.objects.filter(patient=patient).order_by('-date_prescribed')[:5],
            'audit_trail': AuditTrail.objects.filter(patient=patient).order_by('-timestamp')[:5],
            'breadcrumbs': [
                {'label': 'Patients', 'url': reverse('patient_list')},
                {'label': f"{patient.first_name} {patient.last_name}", 'url': None}
            ],
        }

        # Handle AJAX tab loading
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            tab = request.GET.get('tab', 'overview')
            template = f'patient_records/partials/_{tab}.html'
            return render(request, template, context)

        return render(request, 'patient_records/patient_detail.html', context)
        
    except Patient.DoesNotExist:
        messages.error(request, 'Patient not found')
        return redirect('patient_list')

@login_required
def add_diagnosis(request, patient_id):
    """Add diagnosis for a patient"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    breadcrumbs = [
        {'label': 'Patients', 'url': reverse('patient_list')},
        {'label': f'Patient {patient.id}', 'url': reverse('patient_detail', args=[patient.id])},
        {'label': 'Add Diagnosis', 'url': None}
    ]
    
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
    
    context = {
        'form': form,
        'patient': patient,
        'breadcrumbs': breadcrumbs,
        'form_title': 'Add Diagnosis',
        'submit_label': 'Save Diagnosis',
        'cancel_url': reverse('patient_detail', args=[patient.id]),
        'confirmation_message': 'Are you sure you want to save this diagnosis?'
    }
    return render(request, 'patient_records/add_diagnosis.html', context)

@login_required
def add_vitals(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    
    breadcrumbs = [
        {'label': 'Patients', 'url': reverse('patient_list')},
        {'label': f'Patient {patient.id}', 'url': reverse('patient_detail', args=[patient.id])},
        {'label': 'Add Vitals', 'url': None}
    ]
    
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
    
    context = {
        'form': form,
        'patient': patient,
        'breadcrumbs': breadcrumbs,
        'form_title': 'Add Vitals',
        'submit_label': 'Save Vitals',
        'cancel_url': reverse('patient_detail', args=[patient.id]),
        'confirmation_message': 'Are you sure you want to save these vitals?'
    }
    return render(request, 'patient_records/add_vitals.html', context)

@login_required
def add_labs(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    cmp_form = CmpLabsForm()
    cbc_form = CbcLabsForm()
    
    if request.method == 'POST':
        lab_type = request.POST.get('lab_type')
        if lab_type == 'cmp':
            form = CmpLabsForm(request.POST)
        else:
            form = CbcLabsForm(request.POST)
            
        if form.is_valid():
            lab = form.save(commit=False)
            lab.patient = patient
            lab.save()
            messages.success(request, 'Lab results added successfully!')
            return redirect('patient_detail', patient_id=patient_id)
        else:
            if lab_type == 'cmp':
                cmp_form = form
            else:
                cbc_form = form
    
    context = {
        'patient': patient,
        'cmp_form': cmp_form,
        'cbc_form': cbc_form,
        'form_title': 'Add Lab Results',
        'breadcrumbs': [
            {'label': 'Patients', 'url': reverse('patient_list')},
            {'label': str(patient), 'url': reverse('patient_detail', args=[patient.id])},
            {'label': 'Add Labs', 'url': None}
        ]
    }
    return render(request, 'patient_records/add_labs.html', context)

@login_required
def add_medications(request, patient_id):
    """Add medications for a patient"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    breadcrumbs = [
        {'label': 'Patients', 'url': reverse('patient_list')},
        {'label': f'Patient {patient.id}', 'url': reverse('patient_detail', args=[patient.id])},
        {'label': 'Add Medications', 'url': None}
    ]
    
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
    
    context = {
        'form': form,
        'patient': patient,
        'breadcrumbs': breadcrumbs,
        'form_title': 'Add Medication'
    }
    return render(request, 'patient_records/add_medications.html', context)

@login_required
def add_measurements(request, patient_id):
    """Add measurements for a patient"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    breadcrumbs = [
        {'label': 'Patients', 'url': reverse('patient_list')},
        {'label': f'Patient {patient.id}', 'url': reverse('patient_detail', args=[patient.id])},
        {'label': 'Add Measurements', 'url': None}
    ]
    
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
    
    context = {
        'form': form,
        'patient': patient,
        'breadcrumbs': breadcrumbs,
        'form_title': 'Add Measurements'
    }
    return render(request, 'patient_records/add_measurements.html', context)

@login_required
def add_adls(request, patient_id):
    """Add ADLs for a patient"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    breadcrumbs = [
        {'label': 'Patients', 'url': reverse('patient_list')},
        {'label': f'Patient {patient.id}', 'url': reverse('patient_detail', args=[patient.id])},
        {'label': 'Add ADLs', 'url': None}
    ]
    
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
    
    context = {
        'form': form,
        'patient': patient,
        'breadcrumbs': breadcrumbs,
        'form_title': 'Add ADLs'
    }
    return render(request, 'patient_records/add_adls.html', context)

@login_required
def add_symptoms(request, patient_id):
    """Add symptoms for a patient"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    breadcrumbs = [
        {'label': 'Patients', 'url': reverse('patient_list')},
        {'label': f'Patient {patient.id}', 'url': reverse('patient_detail', args=[patient.id])},
        {'label': 'Add Symptoms', 'url': None}
    ]
    
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
    
    context = {
        'form': form,
        'patient': patient,
        'breadcrumbs': breadcrumbs,
        'form_title': 'Add Symptoms'
    }
    return render(request, 'patient_records/add_symptoms.html', context)

@login_required
def add_occurrence(request, patient_id):
    """Add occurrence for a patient"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    breadcrumbs = [
        {'label': 'Patients', 'url': reverse('patient_list')},
        {'label': f'Patient {patient.id}', 'url': reverse('patient_detail', args=[patient.id])},
        {'label': 'Add Occurrence', 'url': None}
    ]
    
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
    
    context = {
        'form': form,
        'patient': patient,
        'breadcrumbs': breadcrumbs,
        'form_title': 'Add Occurrence'
    }
    return render(request, 'patient_records/add_occurrence.html', context)

@login_required
def add_imaging(request, patient_id):
    """Add imaging for a patient"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    breadcrumbs = [
        {'label': 'Patients', 'url': reverse('patient_list')},
        {'label': f'Patient {patient.id}', 'url': reverse('patient_detail', args=[patient.id])},
        {'label': 'Add Imaging', 'url': None}
    ]
    
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
    
    context = {
        'form': form,
        'patient': patient,
        'breadcrumbs': breadcrumbs,
        'form_title': 'Add Imaging'
    }
    return render(request, 'patient_records/add_imaging.html', context)

@login_required
def add_provider(request):
    """Add new provider"""
    breadcrumbs = [
        {'label': 'Providers', 'url': reverse('provider_list')},
        {'label': 'Add Provider', 'url': None}
    ]
    
    if request.method == 'POST':
        form = ProviderForm(request.POST)
        if form.is_valid():
            provider = form.save(commit=False)
            provider.date = datetime.date.today()  # Set today's date
            provider.save()
            messages.success(request, 'Provider added successfully!')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'redirect_url': reverse('provider_list')
                })
            return redirect('provider_list')
        elif request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'errors': form.errors}, status=400)
    else:
        form = ProviderForm()
    
    context = {
        'form': form,
        'breadcrumbs': breadcrumbs,
        'form_title': 'Add Provider',
        'submit_label': 'Save Provider',
        'cancel_url': reverse('provider_list'),
        'confirmation_message': 'Are you sure you want to save this provider?'
    }
    return render(request, 'patient_records/base_form.html', context)

@login_required
def provider_list(request):
    """View list of all providers"""
    breadcrumbs = [
        {'label': 'Providers', 'url': None}
    ]
    
    providers = Provider.objects.all().order_by('provider')
    context = {
        'providers': providers,
        'breadcrumbs': breadcrumbs,
        'page_title': 'Provider List'
    }
    return render(request, 'patient_records/provider_list.html', context)

@login_required
def add_record_request(request, patient_id):
    """Add record request for a patient"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    breadcrumbs = [
        {'label': 'Patients', 'url': reverse('patient_list')},
        {'label': f'Patient {patient.id}', 'url': reverse('patient_detail', args=[patient.id])},
        {'label': 'Add Record Request', 'url': None}
    ]
    
    if request.method == 'POST':
        form = RecordRequestForm(request.POST)
        if form.is_valid():
            record_request = form.save(commit=False)
            record_request.patient = patient
            record_request.save()
            messages.success(request, 'Record request added successfully!')
            return redirect('patient_detail', patient_id=patient_id)
    else:
        form = RecordRequestForm(initial={'patient': patient})
    
    context = {
        'form': form,
        'patient': patient,
        'breadcrumbs': breadcrumbs,
        'form_title': 'Add Record Request'
    }
    return render(request, 'patient_records/add_record_request.html', context)

@login_required
def edit_provider(request, provider_id):
    """Edit existing provider"""
    provider = get_object_or_404(Provider, id=provider_id)
    
    breadcrumbs = [
        {'label': 'Providers', 'url': reverse('provider_list')},
        {'label': 'Edit Provider', 'url': None}
    ]
    
    if request.method == 'POST':
        form = ProviderForm(request.POST, instance=provider)
        if form.is_valid():
            form.save()
            messages.success(request, 'Provider updated successfully!')
            return redirect('provider_list')
    else:
        form = ProviderForm(instance=provider)
    
    context = {
        'form': form,
        'provider': provider,
        'breadcrumbs': breadcrumbs,
        'form_title': f'Edit Provider: {provider}',
        'submit_label': 'Update Provider',
        'cancel_url': reverse('provider_list')
    }
    return render(request, 'patient_records/base_form.html', context)

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    
    def get_success_url(self):
        return '/home/'  # Return absolute URL
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/home/')  # Use absolute URL
        return super().get(request, *args, **kwargs)

def custom_logout(request):
    logout(request)
    return redirect('login')

def your_form_view(request):
    if request.method == 'POST':
        form = YourForm(request.POST)
        if form.is_valid():
            instance = form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'id': instance.id})
            return redirect('success_url')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'errors': form.errors}, status=400)
    else:
        form = YourForm()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('components/modal/_form_modal.html', {'form': form}, request=request)
        return HttpResponse(html)
    
    return render(request, 'your_template.html', {'form': form})

@require_GET
def icd_code_lookup(request):
    query = request.GET.get('q', '').strip().upper()
    if not query:
        return JsonResponse({'results': []})
    
    try:
        # Get the path to the codes.csv file
        csv_path = Path(__file__).parent / 'data' / 'codes.csv'
        
        results = []
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header row if present
            
            for row in csv_reader:
                code = row[0]
                diagnosis = row[4]  # Using the 5th column (index 4) for diagnosis
                if code.startswith(query):
                    results.append({
                        'code': code,
                        'description': diagnosis,  # Changed from row[1] to diagnosis
                        'value': f'{code} - {diagnosis}'  # Updated to use diagnosis
                    })
        
        return JsonResponse({
            'results': results[:5]  # Still limit to 5 results for performance
        })
    except Exception as e:
        logger.error(f"Error in ICD lookup: {str(e)}")
        return JsonResponse({
            'error': 'An error occurred during ICD code lookup'
        }, status=400)

def is_admin(user):
    return user.is_superuser or user.is_staff



@login_required
def patient_tab_data(request, patient_id, tab_name):
    try:
        patient = get_object_or_404(Patient, id=patient_id)
        page = request.GET.get('page', 1)
        items_per_page = 10
        
        if tab_name == 'overview':
            context = {
                'patient': patient,
                'recent_vitals': Vitals.objects.filter(patient=patient).order_by('-date')[:5],
                'recent_medications': Medications.objects.filter(patient=patient).order_by('-date_prescribed')[:5],
            }
            template = 'patient_records/partials/_overview.html'
            
        elif tab_name == 'cmp_labs':
            queryset = CmpLabs.objects.filter(patient=patient).order_by('-date')
            paginator = Paginator(queryset, items_per_page)
            labs = paginator.get_page(page)
            context = {
                'patient': patient,
                'labs': labs,
            }
            template = 'patient_records/partials/_cmp_labs.html'
            
        elif tab_name == 'cbc_labs':
            queryset = CbcLabs.objects.filter(patient=patient).order_by('-date')
            paginator = Paginator(queryset, items_per_page)
            labs = paginator.get_page(page)
            context = {
                'patient': patient,
                'labs': labs,
            }
            template = 'patient_records/partials/_cbc_labs.html'
            
        elif tab_name == 'medications':
            queryset = Medications.objects.filter(patient=patient).order_by('-date_prescribed')
            paginator = Paginator(queryset, items_per_page)
            medications = paginator.get_page(page)
            context = {
                'patient': patient,
                'medications': medications,
            }
            template = 'patient_records/partials/_medications.html'
            
        elif tab_name == 'clinical':
            vitals = Vitals.objects.filter(patient=patient).order_by('-date')
            diagnoses = Diagnosis.objects.filter(patient=patient).order_by('-date')
            symptoms = Symptoms.objects.filter(patient=patient).order_by('-date')
            
            context = {
                'patient': patient,
                'vitals': vitals.all()[:10],  # Latest 10 vitals
                'diagnoses': diagnoses.all()[:10],  # Latest 10 diagnoses
                'symptoms': symptoms.all()[:10],  # Latest 10 symptoms
            }
            template = 'patient_records/partials/_clinical.html'
            
        elif tab_name == 'history':
            try:
                audit_trails = AuditTrail.objects.filter(patient=patient).order_by('-timestamp')
                paginator = Paginator(audit_trails, items_per_page)
                history = paginator.get_page(page)
                
                print(f"History records found: {audit_trails.count()}")
                print(f"Current page: {page}")
                print(f"Has records: {audit_trails.exists()}")
                
                context = {
                    'patient': patient,
                    'history': history,
                    'has_records': audit_trails.exists(),
                    'debug_count': audit_trails.count()
                }
                template = 'patient_records/partials/_history.html'
                
            except Exception as e:
                print(f"Error in history tab: {str(e)}")
                raise
            
        else:
            raise ValueError(f'Unknown tab type: {tab_name}')

        html = render_to_string(template, context, request=request)
        return JsonResponse({
            'html': html,
            'success': True,
            'debug_info': {
                'tab': tab_name,
                'page': page,
                'template': template
            }
        })

    except Exception as e:
        logger.error(f"Error loading tab data: {str(e)}")
        return JsonResponse({
            'error': str(e),
            'success': False
        }, status=500)

@login_required
def medications_api(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    page = request.GET.get('page', 1)
    
    queryset = Medications.objects.filter(patient=patient).order_by('-date_prescribed')
    paginator = Paginator(queryset, 20)
    medications = paginator.get_page(page)
    
    context = {
        'medications': medications,
        'patient': patient,
    }
    
    return JsonResponse({
        'html': render_to_string('patient_records/partials/_medications.html', context),
        'success': True
    })

def patient_history(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    # Get all audit trails for this patient, ordered by most recent
    audit_trails = AuditTrail.objects.filter(patient=patient).order_by('-timestamp')
    
    return render(request, 'patient_records/patient_history.html', {
        'patient': patient,
        'audit_trails': audit_trails
    })