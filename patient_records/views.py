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
from django.db.models import Model, Q
from typing import Optional, Dict, Any
from django.views.decorators.http import require_http_methods
from .forms import VisitsForm, AdlsForm, ImagingForm, RecordRequestLogForm
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

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
    """View list of all patients with advanced search capabilities"""
    search_form = PatientSearchForm(request.GET)
    patients = Patient.objects.all()

    if search_form.is_valid():
        # Basic search
        search = search_form.cleaned_data.get('search')
        if search:
            patients = patients.filter(
                Q(first_name__icontains=search) |
                Q(middle_name__icontains=search) |
                Q(last_name__icontains=search)
            )

        # Patient ID search
        patient_id = search_form.cleaned_data.get('patient_id')
        if patient_id:
            patients = patients.filter(patient_number__icontains=patient_id)

        # ICD Code/Diagnosis search
        diagnosis_text = search_form.cleaned_data.get('diagnosis_text')
        if diagnosis_text:
            patients = patients.filter(diagnosis__diagnosis__iexact=diagnosis_text).distinct()

        # Demographics filters
        age_min = search_form.cleaned_data.get('age_min')
        age_max = search_form.cleaned_data.get('age_max')
        if age_min:
            min_date = timezone.now().date() - timezone.timedelta(days=age_min*365)
            patients = patients.filter(date_of_birth__lte=min_date)
        if age_max:
            max_date = timezone.now().date() - timezone.timedelta(days=age_max*365)
            patients = patients.filter(date_of_birth__gte=max_date)

        gender = search_form.cleaned_data.get('gender')
        if gender:
            patients = patients.filter(gender=gender)

        # Date filters
        date_from = search_form.cleaned_data.get('date_added_from')
        date_to = search_form.cleaned_data.get('date_added_to')
        if date_from:
            patients = patients.filter(date__gte=date_from)
        if date_to:
            patients = patients.filter(date__lte=date_to)

        # Sort options
        sort_by = search_form.cleaned_data.get('sort_by')
        if sort_by:
            patients = patients.order_by(sort_by)
        else:
            patients = patients.order_by('last_name', 'first_name')

    # Pagination
    paginator = Paginator(patients, 10)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage) as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=400)
        page_obj = paginator.get_page(1)

    context = {
        'patients': page_obj,
        'search_form': search_form,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': page_obj,
        'total_patients': patients.count(),
        'breadcrumbs': [{'label': 'Patients', 'url': None}],
        'page_title': 'Patient List'
    }

    # Handle AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('patient_records/partials/_patient_list.html', context, request=request)
        pagination_html = render_to_string('components/_pagination.html', context, request=request)
        results_info = render_to_string('patient_records/partials/_results_info.html', context, request=request)
        return JsonResponse({
            'html': html,
            'pagination': pagination_html,
            'results_info': results_info
        })

    return render(request, 'patient_records/patient_list.html', context)

@login_required
def patient_detail(request, patient_id):
    try:
        # Get patient with all fields
        patient = Patient.objects.get(id=patient_id)
        
        # Create context with processed data
        context = {
            'patient': patient,
            'recent_medications': Medications.objects.filter(
                patient=patient
            ).filter(
                Q(dc_date__isnull=True) | Q(dc_date__gt=datetime.date.today())
            ).order_by('-date_prescribed')[:5],
            'audit_trail': AuditTrail.objects.filter(patient=patient).order_by('-timestamp')[:5],
            'breadcrumbs': [
                {'label': 'Patients', 'url': reverse('patient_list')},
                {'label': f"{patient.first_name} {patient.last_name}", 'url': None}
            ],
            'note_categories': PatientNote.NOTE_CATEGORIES,
            'notes': PatientNote.objects.filter(patient=patient).order_by('-is_pinned', '-created_at')
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

@require_http_methods(["GET", "POST"])
def vital_signs_form(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    
    if request.method == "POST":
        form = VitalsForm(request.POST)
        if form.is_valid():
            vitals = form.save(commit=False)
            vitals.patient = patient
            vitals.save()
            messages.success(request, 'Vital signs recorded successfully!')
            return redirect('patient_detail', patient_id=patient_id)
    else:
        form = VitalsForm()

    context = {
        'form': form,
        'patient': patient,
        'form_title': 'Record Vital Signs',
        'submit_label': 'Save Vital Signs',
        'cancel_url': reverse('patient_detail', args=[patient_id])
    }
    
    return render(request, 'patient_records/add_vitals.html', context)

@login_required
def add_cmp_labs(request, patient_id):
    """Add CMP lab results for a patient"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    if request.method == 'POST':
        form = CMPLabForm(request.POST)
        if form.is_valid():
            lab = form.save(commit=False)
            lab.patient = patient
            lab.save()
            
            create_audit_trail(
                record=lab,
                action='CREATE',
                user=request.user,
                new_values=model_to_dict(lab)
            )
            
            messages.success(request, 'CMP Lab results added successfully!')
            return redirect('patient_detail', patient_id=patient.id)
    else:
        form = CMPLabForm()
    
    context = {
        'patient': patient,
        'cmp_form': form,
        'breadcrumbs': [
            {'label': 'Patients', 'url': reverse('patient_list')},
            {'label': f"{patient.first_name} {patient.last_name}", 'url': reverse('patient_detail', args=[patient.id])},
            {'label': 'Add CMP Labs', 'url': None}
        ],
        'cancel_url': reverse('patient_detail', args=[patient.id])
    }
    return render(request, 'patient_records/add_cmp_labs.html', context)

@login_required
def add_cbc_labs(request, patient_id):
    """Add CBC lab results for a patient"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    if request.method == 'POST':
        form = CBCLabForm(request.POST)
        if form.is_valid():
            lab = form.save(commit=False)
            lab.patient = patient
            lab.save()
            
            create_audit_trail(
                record=lab,
                action='CREATE',
                user=request.user,
                new_values=model_to_dict(lab)
            )
            
            messages.success(request, 'CBC Lab results added successfully!')
            return redirect('patient_detail', patient_id=patient.id)
    else:
        form = CBCLabForm()
    
    context = {
        'patient': patient,
        'cbc_form': form,
        'breadcrumbs': [
            {'label': 'Patients', 'url': reverse('patient_list')},
            {'label': f"{patient.first_name} {patient.last_name}", 'url': reverse('patient_detail', args=[patient.id])},
            {'label': 'Add CBC Labs', 'url': None}
        ],
        'cancel_url': reverse('patient_detail', args=[patient.id])
    }
    return render(request, 'patient_records/add_cbc_labs.html', context)

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
        today = datetime.date.today()
        
        tab_data = {
            'overview': {
                'queryset': None,
                'context': {
                    'recent_vitals': Vitals.objects.filter(patient=patient).order_by('-date')[:5],
                    'recent_medications': Medications.objects.filter(
                        patient=patient
                    ).filter(
                        Q(dc_date__isnull=True) | Q(dc_date__gt=today)
                    ).order_by('-date_prescribed')[:5],
                },
                'template': 'patient_records/partials/_overview.html'
            },
            'visits': {
                'queryset': Visits.objects.filter(patient=patient).order_by('-date'),
                'template': 'patient_records/partials/_visits.html'
            },
            'adls': {
                'queryset': Adls.objects.filter(patient=patient).order_by('-date'),
                'template': 'patient_records/partials/_adls.html'
            },
            'diagnoses': {
                'queryset': Diagnosis.objects.filter(patient=patient).order_by('-date'),
                'template': 'patient_records/partials/_diagnoses.html'
            },
            'cmp_labs': {
                'queryset': CmpLabs.objects.filter(patient=patient).order_by('-date'),
                'template': 'patient_records/partials/_cmp_labs.html',
                'context_name': 'labs',
                'section_title': 'Comprehensive Metabolic Panel (CMP)'
            },
            'cbc_labs': {
                'queryset': CbcLabs.objects.filter(patient=patient).order_by('-date'),
                'template': 'patient_records/partials/_cbc_labs.html',
                'context_name': 'labs',
                'section_title': 'Complete Blood Count (CBC)'
            },
            'vitals': {
                'queryset': Vitals.objects.filter(patient=patient).order_by('-date'),
                'template': 'patient_records/partials/_vitals.html'
            },
            'measurements': {
                'queryset': Measurements.objects.filter(patient=patient).order_by('-date'),
                'template': 'patient_records/partials/_measurements.html'
            },
            'medications': {
                'queryset': Medications.objects.filter(patient=patient).order_by('-date_prescribed'),
                'template': 'patient_records/partials/_medications.html',
                'context_name': 'medications'
            },
            'symptoms': {
                'queryset': Symptoms.objects.filter(patient=patient).order_by('-date'),
                'template': 'patient_records/partials/_symptoms.html'
            },
            'imaging': {
                'queryset': Imaging.objects.filter(patient=patient).order_by('-date'),
                'template': 'patient_records/partials/_imaging.html'
            },
            'occurrences': {
                'queryset': Occurrences.objects.filter(patient=patient).order_by('-date'),
                'template': 'patient_records/partials/_occurrences.html'
            },
            'record_requests': {
                'queryset': RecordRequestLog.objects.filter(patient=patient).order_by('-date'),
                'template': 'patient_records/partials/_record_requests.html'
            }
        }

        tab_info = tab_data.get(tab_name)
        if not tab_info:
            return JsonResponse({'error': 'Invalid tab name'}, status=400)

        context = {'patient': patient}
        
        if tab_info['queryset'] is not None:
            paginator = Paginator(tab_info['queryset'], items_per_page)
            try:
                page_obj = paginator.get_page(page)
                context_name = tab_info.get('context_name', 'records')
                context[context_name] = page_obj
                context['has_records'] = page_obj.paginator.count > 0
            except (PageNotAnInteger, EmptyPage) as e:
                logger.error(f"Pagination error: {str(e)}")
                return JsonResponse({'error': str(e)}, status=400)

        if 'section_title' in tab_info:
            context['section_title'] = tab_info['section_title']

        html = render_to_string(tab_info['template'], context, request=request)
        return JsonResponse({
            'html': html,
            'success': True
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

@require_http_methods(["GET", "POST"])
def add_visit(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == "POST":
        form = VisitsForm(request.POST)
        if form.is_valid():
            visit = form.save(commit=False)
            visit.patient = patient
            visit.save()
            messages.success(request, 'Visit recorded successfully!')
            return redirect('patient_detail', patient_id=patient_id)
    else:
        form = VisitsForm()
    
    return render(request, 'patient_records/add_visit.html', {
        'form': form,
        'patient': patient  # Pass patient to template context
    })

@require_http_methods(["GET", "POST"])
def add_adls(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == "POST":
        form = AdlsForm(request.POST)
        if form.is_valid():
            adls = form.save(commit=False)
            adls.patient = patient
            adls.save()
            messages.success(request, 'ADLs recorded successfully!')
            return redirect('patient_detail', patient_id=patient_id)
    else:
        form = AdlsForm()
    
    return render(request, 'patient_records/add_adls.html', {
        'form': form,
        'patient': patient,
    })

@require_http_methods(["GET", "POST"])
def add_imaging(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == "POST":
        form = ImagingForm(request.POST)
        if form.is_valid():
            imaging = form.save(commit=False)
            imaging.patient = patient
            imaging.save()
            messages.success(request, 'Imaging recorded successfully!')
            return redirect('patient_detail', patient_id=patient_id)
    else:
        form = ImagingForm()
    
    return render(request, 'patient_records/add_imaging.html', {
        'form': form,
        'patient': patient,
    })

@require_http_methods(["GET", "POST"])
def add_record_request(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == "POST":
        form = RecordRequestLogForm(request.POST)
        if form.is_valid():
            record_request = form.save(commit=False)
            record_request.patient = patient
            record_request.save()
            messages.success(request, 'Record request logged successfully!')
            return redirect('patient_detail', patient_id=patient_id)
    else:
        form = RecordRequestLogForm()
    
    return render(request, 'patient_records/add_record_request.html', {
        'form': form,
        'patient': patient,
    })

@login_required
def patient_notes(request, patient_id):
    """Get all notes for a patient"""
    patient = get_object_or_404(Patient, id=patient_id)
    notes = PatientNote.objects.filter(patient=patient)
    
    context = {
        'patient': patient,
        'notes': notes,
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('patient_records/partials/_notes_list.html', context)
        return JsonResponse({'html': html})
    
    return render(request, 'patient_records/notes.html', context)

@login_required
def create_note(request):
    """Create a new patient note"""
    if request.method == 'POST':
        try:
            # Get patient ID from form data
            patient_id = request.POST.get('patient')
            if not patient_id:
                return JsonResponse({
                    'success': False,
                    'errors': {'patient': ['Patient ID is required']}
                }, status=400)

            # Get patient instance
            try:
                patient = Patient.objects.get(id=patient_id)
            except Patient.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'errors': {'patient': ['Invalid patient ID']}
                }, status=400)
            
            # Create form instance with files
            post_data = request.POST.copy()  # Make a mutable copy
            post_data['patient'] = patient.id  # Ensure patient ID is in form data
            
            form = PatientNoteForm(post_data, request.FILES)
            
            if form.is_valid():
                note = form.save(commit=False)
                note.patient = patient
                note.created_by = request.user
                note.save()
                
                # Save tags
                if 'tags' in form.cleaned_data:
                    tags = form.cleaned_data['tags']
                    if isinstance(tags, str):
                        # Split by comma and strip whitespace
                        tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
                    for tag_name in tags:
                        tag, _ = NoteTag.objects.get_or_create(name=tag_name)
                        note.tags.add(tag)
                
                # Handle file attachments
                files = request.FILES.getlist('attachments')
                for file in files:
                    NoteAttachment.objects.create(note=note, file=file)

                return JsonResponse({
                    'success': True,
                    'noteId': note.id,
                    'message': 'Note created successfully'
                })
            else:
                print("Form validation errors:", form.errors)  # Debug print
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
                
        except Exception as e:
            import traceback
            print(f"Error creating note: {str(e)}")
            print(traceback.format_exc())  # Print full traceback
            return JsonResponse({
                'success': False,
                'errors': {'__all__': ['An error occurred while creating the note']}
            }, status=500)
    else:
        form = PatientNoteForm()
        html = render_to_string('patient_records/partials/_note_form.html', {
            'form': form,
            'form_title': 'Create New Note'
        })
        return JsonResponse({
            'success': True,
            'html': html
        })

@login_required
def edit_note(request, note_id):
    """Edit an existing patient note"""
    note = get_object_or_404(PatientNote, id=note_id)
    if request.method == 'POST':
        form = PatientNoteForm(request.POST, request.FILES, instance=note)
        if form.is_valid():
            note = form.save()
            
            # Handle tags
            if 'tags' in form.cleaned_data:
                note.tags.clear()
                tags = form.cleaned_data['tags']
                if isinstance(tags, str):
                    tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
                for tag_name in tags:
                    tag, _ = NoteTag.objects.get_or_create(name=tag_name)
                    note.tags.add(tag)
            
            # Handle attachments
            files = request.FILES.getlist('attachments')
            for file in files:
                NoteAttachment.objects.create(note=note, file=file)
            
            return JsonResponse({
                'success': True,
                'noteId': note.id,
                'message': 'Note updated successfully'
            })
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)
    else:
        # Return note data for editing
        return JsonResponse({
            'success': True,
            'note': {
                'title': note.title,
                'category': note.category,
                'content': note.content,
                'tags': [tag.name for tag in note.tags.all()],
                'is_pinned': note.is_pinned
            }
        })

@login_required
def delete_note(request, note_id):
    """Delete a patient note"""
    if request.method == 'POST':
        note = get_object_or_404(PatientNote, id=note_id)
        note.delete()
        return JsonResponse({
            'success': True,
            'message': 'Note deleted successfully'
        })
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=400)

@login_required
def note_detail(request, note_id):
    """Get note details"""
    note = get_object_or_404(PatientNote, id=note_id)
    html = render_to_string('patient_records/partials/_note_detail.html', {
        'note': note
    })
    return JsonResponse({
        'success': True,
        'html': html
    })

@login_required
def toggle_pin_note(request, note_id):
    """Toggle pin status of a note"""
    note = get_object_or_404(PatientNote, id=note_id)
    note.is_pinned = not note.is_pinned
    note.save()
    return JsonResponse({
        'success': True,
        'message': f'Note {"pinned" if note.is_pinned else "unpinned"} successfully'
    })

@login_required
def patient_notes(request):
    """Get filtered notes list"""
    patient_id = request.GET.get('patient')
    category = request.GET.get('category')
    
    notes = PatientNote.objects.all()
    if patient_id:
        notes = notes.filter(patient_id=patient_id)
    if category:
        notes = notes.filter(category=category)
    
    notes = notes.order_by('-is_pinned', '-created_at')
    
    html = render_to_string('patient_records/partials/_notes_list.html', {
        'notes': notes
    })
    return JsonResponse({
        'success': True,
        'html': html,
        'count': notes.count()
    })

@login_required
def get_note_detail(request, note_id):
    """Get note details for quick view"""
    note = get_object_or_404(PatientNote, id=note_id)
    return JsonResponse({
        'success': True,
        'note': {
            'title': note.title,
            'content': note.content,
            'category_display': note.get_category_display(),
            'is_pinned': note.is_pinned,
            'tags': [tag.name for tag in note.tags.all()],
            'attachments': [{
                'url': attachment.file.url,
                'filename': attachment.file.name.split('/')[-1]
            } for attachment in note.attachments.all()],
            'created_by': note.created_by.get_full_name() if note.created_by else 'Unknown',
            'created_at': note.created_at.strftime('%Y-%m-%d %H:%M %p'),
            'updated_at': note.updated_at.strftime('%Y-%m-%d %H:%M %p')
        }
    })