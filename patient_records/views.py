"""Views for patient records."""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.core.paginator import Paginator
from django.urls import reverse
from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_GET
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.core.exceptions import ValidationError
import logging
import json
import datetime
import decimal
import uuid
from typing import Dict, Optional, Any
from django.db.models import Model
from django.contrib.auth.models import User
from patient_records.models import AuditTrail

# Import models explicitly instead of using wildcard
from .models.patient import Patient, Provider
from .models.clinical import (
    Vitals, Diagnosis, Medications, PatientNote, NoteTag,
    CmpLabs, CbcLabs, Symptoms, Imaging, Adls, Occurrences,
    ClinicalNote, Measurements, Visits
)
from .models.audit import AuditTrail, EventStore, RecordRequestLog
from .models.read import ClinicalReadModel, PatientReadModel, LabResultsReadModel

# Import forms
from .forms import (
    PatientForm, 
    ProviderForm, 
    VitalsForm,
    CMPLabForm, 
    CBCLabForm, 
    PatientNoteForm,
    NoteAttachmentForm, 
    MeasurementsForm,
    SymptomsForm, 
    ImagingForm, 
    AdlsForm,
    OccurrencesForm, 
    DiagnosisForm, 
    VisitsForm,
    MedicationsForm, 
    RecordRequestLogForm,
    PatientSearchForm
)

# Set up logging
logger = logging.getLogger(__name__)

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    
    def get_success_url(self):
        return '/home/'  # Return absolute URL
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/home/')  # Use absolute URL
        return super().get(request, *args, **kwargs)

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
        elif isinstance(value, uuid.UUID):  # Handle UUIDs
            serialized[key] = str(value)
        else:
            serialized[key] = value
    return serialized

def serialize_model_instance(
    record: Model,
    exclude_fields: list = None,
    include_fields: list = None
) -> Dict:
    """Serialize model instance for JSON response."""
    serialized = {}
    for field in record._meta.fields:
        if field.name in (exclude_fields or []) or (include_fields and field.name not in include_fields):
            continue
        value = getattr(record, field.name)
        if isinstance(value, (datetime.date, datetime.datetime)):
            serialized[field.name] = value.isoformat()
        elif isinstance(value, decimal.Decimal):
            serialized[field.name] = float(value)
        elif isinstance(value, uuid.UUID):
            serialized[field.name] = str(value)
        else:
            serialized[field.name] = value
    return serialized

def create_audit_trail(
    record: Model,
    action: str,
    user: User,
    previous_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    record_type: Optional[str] = None
) -> AuditTrail:
    """
    Create an audit trail entry with enhanced logging
    """
    try:
        model_name = record_type or record.__class__.__name__.upper()
        logger.info(f"Creating audit trail - Action: {action}, Model: {model_name}, Record ID: {record.id}")
        
        # Serialize the values before storage
        previous_values = serialize_model_data(previous_values) if previous_values else {}
        new_values = serialize_model_data(new_values) if new_values else {}

        # Create audit trail
        audit = AuditTrail.objects.create(
            patient=record if isinstance(record, Patient) else None,
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
            patient = form.save()  # Save directly since no modifications needed
            
            # Create audit trail with proper record type
            create_audit_trail(
                record=patient,
                user=request.user,
                action='CREATE',
                new_values=model_to_dict(patient)
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
    search_form = PatientSearchForm(request.GET or None)
    patients = Patient.objects.all().order_by('-updated_at')  # Default sort
    
    if search_form.is_valid():
        active_filters = search_form.get_active_filters()
        
        # Basic search
        if 'search' in active_filters:
            search = active_filters['search']
            search_terms = search.split()
            query = Q()
            for term in search_terms:
                term_query = (
                    Q(first_name__icontains=term) |
                    Q(middle_name__icontains=term) |
                    Q(last_name__icontains=term) |
                    Q(patient_number__icontains=term)
                )
                query |= term_query
            patients = patients.filter(query)

        # Patient ID search
        if 'patient_id' in active_filters:
            patient_id = active_filters['patient_id']
            patients = patients.filter(patient_number__icontains=patient_id)

        # Gender filter
        if 'gender' in active_filters:
            gender = active_filters['gender']
            patients = patients.filter(gender=gender)

        # Date range filter
        if 'date_added_from' in active_filters:
            from_date = active_filters['date_added_from']
            from_datetime = timezone.make_aware(datetime.datetime.combine(from_date, datetime.time.min))
            patients = patients.filter(created_at__gte=from_datetime)
            
        if 'date_added_to' in active_filters:
            to_date = active_filters['date_added_to']
            to_datetime = timezone.make_aware(datetime.datetime.combine(to_date, datetime.time.max))
            patients = patients.filter(created_at__lte=to_datetime)

        # Age range filter
        today = timezone.now().date()
        
        if 'age_min' in active_filters:
            age_min = active_filters['age_min']
            max_birth_date = today - timezone.timedelta(days=age_min * 365)
            patients = patients.filter(date_of_birth__lte=max_birth_date)
            
        if 'age_max' in active_filters:
            age_max = active_filters['age_max']
            min_birth_date = today - timezone.timedelta(days=age_max * 365)
            patients = patients.filter(date_of_birth__gte=min_birth_date)

        # Sort handling
        if 'sort_by' in active_filters:
            sort_by = active_filters['sort_by']
            patients = patients.order_by(sort_by)

    # Pagination
    paginator = Paginator(patients, 10)  # Show 10 patients per page
    page = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            page_obj = paginator.page(paginator.num_pages)
        else:
            page_obj = paginator.page(1)

    context = {
        'search_form': search_form,
        'patients': page_obj,
        'total_patients': paginator.count,
        'page_obj': page_obj,
        'paginator': paginator,
        'breadcrumbs': [{'label': 'Patients', 'url': None}],
        'is_paginated': paginator.num_pages > 1
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('patient_records/patient_list_content.html', context, request)
        return JsonResponse({'html': html})

    return render(request, 'patient_records/patient_list.html', context)

@login_required
def patient_detail(request, patient_id):
    """
    Display detailed patient information with optimized queries and caching
    """
    try:
        logger.info(f"Loading patient detail for ID: {patient_id}")
        
        # Get patient with optimized queries
        patient = get_object_or_404(Patient, id=patient_id)
        logger.info(f"Found patient: {patient.first_name} {patient.last_name}")
        
        # Get all related data in optimized queries
        try:
            # Get recent vitals with proper ordering
            recent_vitals = Vitals.objects.filter(
                patient=patient
            ).select_related('patient').order_by('-date')[:10]
            
            logger.info(f"Found {recent_vitals.count()} recent vitals records")
            if recent_vitals:
                logger.info(f"Most recent vitals from {recent_vitals[0].date}")
            else:
                logger.info("No vitals found for patient")
        except Exception as e:
            logger.error(f"Error querying vitals: {str(e)}")
            recent_vitals = Vitals.objects.none()
        
        try:
            active_diagnoses = Diagnosis.objects.filter(
                patient=patient
            ).select_related('provider').order_by('-date')
            logger.info(f"Found {active_diagnoses.count()} diagnoses")
        except Exception as e:
            logger.error(f"Error querying diagnoses: {str(e)}")
            active_diagnoses = Diagnosis.objects.none()
        
        try:
            current_medications = Medications.objects.filter(
                patient=patient
            ).filter(
                Q(dc_date__isnull=True) | Q(dc_date__gt=timezone.now().date())
            ).select_related().order_by('-date_prescribed')
            logger.info(f"Found {current_medications.count()} current medications")
        except Exception as e:
            logger.error(f"Error querying medications: {str(e)}")
            current_medications = Medications.objects.none()
        
        try:
            recent_activities = EventStore.objects.filter(
                aggregate_id=str(patient_id),
                event_type__in=['RECORD_CREATED', 'RECORD_UPDATED', 'STATUS_CHANGED']
            ).order_by('-timestamp')[:10]
            logger.info("Successfully queried recent activities")
        except Exception as e:
            logger.error(f"Error querying audit trail: {str(e)}")
            recent_activities = EventStore.objects.none()
        
        try:
            notes = PatientNote.objects.filter(
                patient=patient
            ).select_related('created_by').prefetch_related(
                'tags',
                'attachments'
            ).order_by('-is_pinned', '-created_at')
            logger.info(f"Found {notes.count()} patient notes")
        except Exception as e:
            logger.error(f"Error querying notes: {str(e)}")
            notes = PatientNote.objects.none()
        
        # Create context with all required data
        context = {
            'patient': patient,
            'recent_vitals': recent_vitals,
            'current_medications': current_medications,
            'active_diagnoses': active_diagnoses,
            'cbc_labs': CbcLabs.objects.filter(patient=patient).order_by('-date')[:5],
            'cmp_labs': CmpLabs.objects.filter(patient=patient).order_by('-date')[:5],
            'symptoms': Symptoms.objects.filter(patient=patient).order_by('-date')[:5],
            'visits': Visits.objects.filter(patient=patient).order_by('-date')[:5],
            'measurements': Measurements.objects.filter(patient=patient).order_by('-date')[:5],
            'adls': Adls.objects.filter(patient=patient).order_by('-date')[:5],
            'imaging': Imaging.objects.filter(patient=patient).order_by('-date')[:5],
            'occurrences': Occurrences.objects.filter(patient=patient).order_by('-date')[:5],
            'record_requests': RecordRequestLog.objects.filter(patient=patient).order_by('-date')[:5],
            'recent_activities': recent_activities,
            'notes': notes,
            'breadcrumbs': [
                {'label': 'Patients', 'url': reverse('patient_list')},
                {'label': f"{patient.first_name} {patient.last_name}", 'url': None}
            ],
            'note_categories': PatientNote.NOTE_CATEGORIES,
        }

        # Handle AJAX tab loading
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            tab = request.GET.get('tab', 'overview')
            template = f'patient_records/partials/_{tab}.html'
            return render(request, template, context)

        response = render(request, 'patient_records/patient_detail.html', context)
        return response
        
    except Patient.DoesNotExist:
        logger.error(f"Patient not found with ID: {patient_id}")
        messages.error(request, 'Patient not found')
        return redirect('patient_list')
    except Exception as e:
        logger.error(f"Error in patient_detail view: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred while loading patient details')
        return redirect('patient_list')

@login_required
def add_diagnosis(request, patient_id):
    """Add diagnosis for a patient"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    if request.method == 'POST':
        logger.debug(f'Processing diagnosis form submission for patient {patient_id}')
        form = DiagnosisForm(request.POST, user=request.user)
        if form.is_valid():
            logger.debug(f'Diagnosis form is valid. Data: {form.cleaned_data}')
            diagnosis = form.save(commit=False)
            diagnosis.patient = patient
            diagnosis.save()
            
            # Create event store entry
            event_store = EventStoreService()
            event_data = {
                'patient_id': patient_id,
                'diagnosis_id': str(diagnosis.id),
                'date': diagnosis.date.isoformat(),
                'icd_code': diagnosis.icd_code,
                'diagnosis': diagnosis.diagnosis,
                'notes': diagnosis.notes,
                'source': diagnosis.source
            }
            event_store.append_event(
                aggregate_id=str(patient_id),
                aggregate_type=CLINICAL_AGGREGATE,
                event_type=DIAGNOSIS_ADDED,
                event_data=event_data
            )
            
            messages.success(request, 'Diagnosis added successfully!')
            return redirect('patient_detail', patient_id=patient_id)
        else:
            logger.error(f'Diagnosis form validation failed. Errors: {form.errors}')
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DiagnosisForm(initial={'patient': patient}, user=request.user)
    
    context = {
        'form': form,
        'patient': patient,
        'breadcrumbs': [
            {'label': 'Patients', 'url': reverse('patient_list')},
            {'label': f'Patient {patient.id}', 'url': reverse('patient_detail', args=[patient.id])},
            {'label': 'Add Diagnosis', 'url': None}
        ],
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
        try:
            logger.debug(f'Processing vitals form submission for patient {patient_id}')
            logger.debug(f'POST data: {request.POST}')
            
            form = VitalsForm(request.POST, user=request.user)
            if form.is_valid():
                logger.debug(f'Vitals form is valid. Data: {form.cleaned_data}')
                vitals = form.save(commit=False)
                vitals.patient = patient
                vitals.save()
                
                # Create audit trail
                create_audit_trail(
                    record=vitals,
                    user=request.user,
                    action='CREATE',
                    new_values=model_to_dict(vitals),
                    record_type='VITALS'
                )
                
                messages.success(request, 'Vital signs recorded successfully!')
                return redirect('patient_detail', patient_id=patient_id)
            else:
                logger.error(f'Vitals form validation failed. Errors: {form.errors}')
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
        except Exception as e:
            logger.error(f'Error saving vitals: {str(e)}', exc_info=True)
            messages.error(request, 'An error occurred while saving vitals. Please try again.')
    else:
        form = VitalsForm(user=request.user)

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
        form = CMPLabForm(request.POST, user=request.user)
        if form.is_valid():
            lab = form.save(commit=False)
            lab.patient = patient
            lab.modified_by = request.user
            lab.save()
            
            create_audit_trail(
                record=lab,
                user=request.user,
                action='CREATE',
                changes={'new_values': model_to_dict(lab), 'record_type': 'CMP_LAB'}
            )
            
            messages.success(request, 'CMP Lab results added successfully!')
            return redirect('patient_detail', patient_id=patient.id)
    else:
        form = CMPLabForm(user=request.user)
    
    context = {
        'patient': patient,
        'form': form,  # Changed from cmp_form to form for consistency
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
        form = CBCLabForm(request.POST, user=request.user)
        if form.is_valid():
            lab = form.save(commit=False)
            lab.patient = patient
            lab.modified_by = request.user
            lab.save()
            
            create_audit_trail(
                record=lab,
                user=request.user,
                action='CREATE',
                changes={'new_values': model_to_dict(lab), 'record_type': 'CBC_LAB'}
            )
            
            messages.success(request, 'CBC Lab results added successfully!')
            return redirect('patient_detail', patient_id=patient.id)
    else:
        form = CBCLabForm(user=request.user)
    
    context = {
        'patient': patient,
        'form': form,  # Changed from cbc_form to form
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
    
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Handle empty dc_date
            post_data = request.POST.copy()
            if 'dc_date' in post_data and (not post_data['dc_date'] or post_data['dc_date'].strip() == ''):
                post_data.pop('dc_date')  # Remove empty dc_date from the data
            
            form = MedicationsForm(post_data, user=request.user)
            
            if form.is_valid():
                med = form.save(commit=False)
                med.patient = patient
                med.date = form.cleaned_data['date_prescribed']
                # Only set dc_date if it was actually provided
                med.dc_date = form.cleaned_data.get('dc_date') if 'dc_date' in post_data else None
                med.save()
                
                # Create audit trail
                create_audit_trail(
                    record=med,
                    user=request.user,
                    action='CREATE',
                    new_values=model_to_dict(med),
                    record_type='MEDICATIONS'
                )
                
                messages.success(request, 'Medication added successfully!')
                return JsonResponse({'success': True, 'redirect': reverse('patient_detail', args=[patient_id])})
            else:
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        except ValidationError as e:
            return JsonResponse({'success': False, 'errors': e.message_dict}, status=400)
        except Exception as e:
            logger.error(f'Error saving medication: {str(e)}', exc_info=True)
            return JsonResponse({'success': False, 'errors': {'__all__': ['An error occurred while saving medication.']}}, status=500)
    elif request.method == 'POST':
        try:
            # Handle empty dc_date
            post_data = request.POST.copy()
            if 'dc_date' in post_data and (not post_data['dc_date'] or post_data['dc_date'].strip() == ''):
                post_data.pop('dc_date')  # Remove empty dc_date from the data
            
            form = MedicationsForm(post_data, user=request.user)
            
            if form.is_valid():
                med = form.save(commit=False)
                med.patient = patient
                med.date = form.cleaned_data['date_prescribed']
                # Only set dc_date if it was actually provided
                med.dc_date = form.cleaned_data.get('dc_date') if 'dc_date' in post_data else None
                med.save()
                
                # Create audit trail
                create_audit_trail(
                    record=med,
                    user=request.user,
                    action='CREATE',
                    new_values=model_to_dict(med),
                    record_type='MEDICATIONS'
                )
                
                messages.success(request, 'Medication added successfully!')
                return redirect('patient_detail', patient_id=patient_id)
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
        except ValidationError as e:
            for field, errors in e.message_dict.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
        except Exception as e:
            logger.error(f'Error saving medication: {str(e)}', exc_info=True)
            messages.error(request, 'An error occurred while saving medication. Please try again.')
    else:
        form = MedicationsForm(initial={'patient': patient}, user=request.user)
    
    context = {
        'form': form,
        'patient': patient,
        'breadcrumbs': [
            {'label': 'Patients', 'url': reverse('patient_list')},
            {'label': f'Patient {patient.id}', 'url': reverse('patient_detail', args=[patient.id])},
            {'label': 'Add Medication', 'url': None}
        ]
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
        form = MeasurementsForm(request.POST, user=request.user)
        if form.is_valid():
            measurement = form.save(commit=False)
            measurement.patient = patient
            measurement.save()
            messages.success(request, 'Measurements added successfully!')
            return redirect('patient_detail', patient_id=patient_id)
    else:
        form = MeasurementsForm(initial={'patient': patient}, user=request.user)
    
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
        form = AdlsForm(request.POST, user=request.user)
        if form.is_valid():
            adls = form.save(commit=False)
            adls.patient = patient
            adls.save()
            messages.success(request, 'ADLs added successfully!')
            return redirect('patient_detail', patient_id=patient_id)
    else:
        form = AdlsForm(initial={'patient': patient}, user=request.user)
    
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
    
    if request.method == 'POST':
        logger.debug(f'Processing symptoms form submission for patient {patient_id}')
        form = SymptomsForm(request.POST, user=request.user)
        if form.is_valid():
            logger.debug(f'Symptoms form is valid. Data: {form.cleaned_data}')
            symptoms = form.save(commit=False)
            symptoms.patient = patient
            symptoms.save()
            
            messages.success(request, 'Symptoms added successfully!')
            return redirect('patient_detail', patient_id=patient_id)
        else:
            logger.error(f'Symptoms form validation failed. Errors: {form.errors}')
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SymptomsForm(initial={'patient': patient}, user=request.user)
    
    context = {
        'form': form,
        'patient': patient,
        'breadcrumbs': [
            {'label': 'Patients', 'url': reverse('patient_list')},
            {'label': f'Patient {patient.id}', 'url': reverse('patient_detail', args=[patient.id])},
            {'label': 'Add Symptoms', 'url': None}
        ],
        'form_title': 'Add Symptoms',
        'submit_label': 'Save Symptoms',
        'cancel_url': reverse('patient_detail', args=[patient.id]),
        'confirmation_message': 'Are you sure you want to save these symptoms?'
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
        form = OccurrencesForm(request.POST, user=request.user)
        if form.is_valid():
            occurrence = form.save(commit=False)
            occurrence.patient = patient
            occurrence.save()
            messages.success(request, 'Occurrence added successfully!')
            return redirect('patient_detail', patient_id=patient_id)
    else:
        form = OccurrencesForm(initial={'patient': patient}, user=request.user)
    
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
        form = ImagingForm(request.POST, user=request.user)
        if form.is_valid():
            imaging = form.save(commit=False)
            imaging.patient = patient
            imaging.save()
            messages.success(request, 'Imaging added successfully!')
            return redirect('patient_detail', patient_id=patient_id)
    else:
        form = ImagingForm(initial={'patient': patient}, user=request.user)
    
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
        form = RecordRequestLogForm(request.POST, user=request.user)
        if form.is_valid():
            record_request = form.save(commit=False)
            record_request.patient = patient
            record_request.save()
            messages.success(request, 'Record request added successfully!')
            return redirect('patient_detail', patient_id=patient_id)
    else:
        form = RecordRequestLogForm(initial={'patient': patient}, user=request.user)
    
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
        
        # Get the latest clinical read model for symptoms and provider data
        latest_clinical_data = (ClinicalReadModel.objects
            .filter(patient_id=patient.id)
            .order_by('-recorded_at')
            .first())
        
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
                    'latest_clinical_data': latest_clinical_data
                },
                'template': 'patient_records/partials/_overview.html'
            },
            'visits': {
                'queryset': Visits.objects.filter(patient=patient).order_by('-date'),
                'template': 'patient_records/partials/_visits.html',
                'context': {
                    'latest_clinical_data': latest_clinical_data
                }
            },
            'symptoms': {
                'queryset': Symptoms.objects.filter(patient=patient).order_by('-date'),
                'template': 'patient_records/partials/_symptoms.html',
                'context': {
                    'latest_clinical_data': latest_clinical_data,
                    'symptoms_summary': latest_clinical_data.symptoms_summary if latest_clinical_data else None,
                    'provider_details': latest_clinical_data.provider_details if latest_clinical_data else None
                }
            },
            'diagnoses': {
                'queryset': Diagnosis.objects.filter(patient=patient).order_by('-date'),
                'template': 'patient_records/partials/_diagnoses.html',
                'context': {
                    'latest_clinical_data': latest_clinical_data
                }
            }
        }

        tab_info = tab_data.get(tab_name)
        if not tab_info:
            return JsonResponse({'error': 'Invalid tab name'}, status=400)

        context = {'patient': patient}
        
        # Add any additional context from tab_info
        if 'context' in tab_info:
            context.update(tab_info['context'])
        
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
                
        # Add default values for empty fields
        context['default_provider'] = {'name': 'Not Specified', 'practice': 'Not Available'}
        context['default_symptom'] = {'description': 'No symptoms recorded', 'severity': 'N/A'}
        
        html = render_to_string(tab_info['template'], context, request=request)
        return JsonResponse({'html': html})

    except Exception as e:
        logger.error(f"Error loading tab data: {str(e)}")
        return JsonResponse({
            'error': str(e),
            'success': False
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_medications(request, patient_id):
    """Get medications for a patient."""
    try:
        # Validate patient ID
        try:
            patient_uuid = uuid.UUID(str(patient_id))
        except ValueError:
            return JsonResponse({'error': 'Invalid patient ID'}, status=400)
        
        # Get patient and medications
        try:
            patient = Patient.objects.get(id=patient_uuid)
        except Patient.DoesNotExist:
            return JsonResponse({'error': 'Patient not found'}, status=404)
        
        medications = Medications.objects.filter(patient=patient).order_by('-date_prescribed')
        
        # Serialize medications
        data = []
        for med in medications:
            data.append({
                'id': str(med.id),
                'drug': med.drug,
                'dose': med.dose,
                'frequency': med.frequency,
                'route': med.route,
                'date_prescribed': med.date_prescribed.isoformat(),
                'dc_date': med.dc_date.isoformat() if med.dc_date else None,
                'notes': med.notes,
                'prn': med.prn
            })
        
        return JsonResponse({'medications': data}, encoder=DjangoJSONEncoder)
    except Exception as e:
        logger.error(f"Error in get_medications: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

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
        form = VisitsForm(request.POST, user=request.user)
        if form.is_valid():
            visit = form.save(commit=False)
            visit.patient = patient
            visit.save()
            
            success_message = 'Visit recorded successfully!'
            messages.success(request, success_message)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': success_message,
                    'redirect': reverse('patient_detail', args=[patient_id])
                })
            return redirect('patient_detail', patient_id=patient_id)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
    else:
        form = VisitsForm(user=request.user)
    
    context = {
        'form': form,
        'patient': patient,
        'form_title': 'Add Visit',
        'submit_label': 'Save Visit',
        'cancel_url': reverse('patient_detail', args=[patient_id])
    }
    return render(request, 'patient_records/add_visit.html', context)

@require_http_methods(["GET", "POST"])
def add_adls(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == "POST":
        form = AdlsForm(request.POST, user=request.user)
        if form.is_valid():
            adls = form.save(commit=False)
            adls.patient = patient
            adls.save()
            messages.success(request, 'ADLs recorded successfully!')
            return redirect('patient_detail', patient_id=patient_id)
    else:
        form = AdlsForm(initial={'patient': patient}, user=request.user)
    
    return render(request, 'patient_records/add_adls.html', {
        'form': form,
        'patient': patient,
    })

@require_http_methods(["GET", "POST"])
def add_imaging(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == "POST":
        form = ImagingForm(request.POST, user=request.user)
        if form.is_valid():
            imaging = form.save(commit=False)
            imaging.patient = patient
            imaging.save()
            messages.success(request, 'Imaging recorded successfully!')
            return redirect('patient_detail', patient_id=patient_id)
    else:
        form = ImagingForm(initial={'patient': patient}, user=request.user)
    
    return render(request, 'patient_records/add_imaging.html', {
        'form': form,
        'patient': patient,
    })

@require_http_methods(["GET", "POST"])
def add_record_request(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == "POST":
        form = RecordRequestLogForm(request.POST, user=request.user)
        if form.is_valid():
            record_request = form.save(commit=False)
            record_request.patient = patient
            record_request.save()
            messages.success(request, 'Record request logged successfully!')
            return redirect('patient_detail', patient_id=patient_id)
    else:
        form = RecordRequestLogForm(initial={'patient': patient}, user=request.user)
    
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

@login_required
def overview_dashboard(request):
    """View for the overview dashboard"""
    context = {
        'breadcrumbs': [
            {'label': 'Dashboards', 'url': None},
            {'label': 'Overview', 'url': None}
        ],
        'page_title': 'Overview Dashboard'
    }
    return render(request, 'dashboards/overview_dashboard.html', context)

@login_required
def dashboard_data(request):
    """API endpoint for dashboard data"""
    try:
        # Get date range from request
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # Convert to datetime objects
        start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Get metrics
        metrics = {
            'total_visits': Visits.objects.filter(date__range=[start_date, end_date]).count(),
            'active_medications': Medications.objects.filter(
                Q(dc_date__isnull=True) | Q(dc_date__gt=timezone.now())
            ).count(),
            'recent_labs': CmpLabs.objects.filter(date__range=[start_date, end_date]).count(),
            'pending_tasks': RecordRequestLog.objects.filter(
                status='pending',
                date__range=[start_date, end_date]
            ).count()
        }
        
        # Get vitals data
        vitals = Vitals.objects.filter(date__range=[start_date, end_date]).order_by('date')
        vitals_data = {
            'dates': [v.date.isoformat() for v in vitals],
            'systolic': [v.systolic for v in vitals],
            'diastolic': [v.diastolic for v in vitals],
            'heartRate': [v.pulse for v in vitals]
        }
        
        # Get recent activities
        activities = EventStore.objects.filter(
            aggregate_id=str(patient_id),
            event_type__in=['RECORD_CREATED', 'RECORD_UPDATED', 'STATUS_CHANGED']
        ).order_by('-timestamp')[:10]
        activities_data = [{
            'timestamp': activity.timestamp.isoformat(),
            'action': activity.action,
            'description': f"{activity.record_type} - {activity.patient_identifier}"
        } for activity in activities]
        
        # Generate alerts
        alerts = []
        
        # Check for abnormal vitals
        recent_vitals = Vitals.objects.filter(date__range=[start_date, end_date])
        for vital in recent_vitals:
            if vital.systolic > 180 or vital.diastolic > 110:
                alerts.append({
                    'severity': 'high',
                    'message': f'High blood pressure reading: {vital.blood_pressure} on {vital.date}'
                })
            elif vital.temperature > 38.3:  # >101°F
                alerts.append({
                    'severity': 'high',
                    'message': f'High temperature: {vital.temperature}°C on {vital.date}'
                })
        
        # Check for pending record requests
        pending_requests = RecordRequestLog.objects.filter(
            status='pending',
            date__range=[start_date, end_date]
        )
        if pending_requests.exists():
            alerts.append({
                'severity': 'medium',
                'message': f'{pending_requests.count()} pending record requests'
            })
        
        return JsonResponse({
            'metrics': metrics,
            'vitals': vitals_data,
            'activities': activities_data,
            'alerts': alerts
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=400)

@login_required
def get_latest_vitals(request, patient_id):
    """API endpoint for latest vitals data"""
    try:
        patient = get_object_or_404(Patient, id=patient_id)
        
        # Get latest vitals
        latest_vitals = Vitals.objects.filter(patient=patient).order_by('-date').first()
        
        # Get vitals history for chart
        vitals_history = Vitals.objects.filter(
            patient=patient,
            date__gte=timezone.now() - timezone.timedelta(days=30)  # Last 30 days
        ).order_by('date')
        
        history_data = [{
            'date': vital.date.isoformat(),
            'systolic': vital.systolic,
            'diastolic': vital.diastolic,
            'heart_rate': vital.pulse
        } for vital in vitals_history]
        
        if latest_vitals:
            data = {
                'systolic': latest_vitals.systolic,
                'diastolic': latest_vitals.diastolic,
                'heart_rate': latest_vitals.pulse,
                'history': history_data
            }
        else:
            data = {
                'systolic': None,
                'diastolic': None,
                'heart_rate': None,
                'history': []
            }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_latest_labs(request, patient_id):
    """API endpoint for latest labs data"""
    try:
        patient = get_object_or_404(Patient, id=patient_id)
        
        # Get latest CMP labs
        latest_cmp = CmpLabs.objects.filter(patient=patient).order_by('-date').first()
        
        # Get latest CBC labs
        latest_cbc = CbcLabs.objects.filter(patient=patient).order_by('-date').first()
        
        data = {
            'glucose': latest_cmp.glucose if latest_cmp else None,
            'wbc': latest_cbc.wbc if latest_cbc else None
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_latest_measurements(request, patient_id):
    """API endpoint for latest measurements data"""
    try:
        patient = get_object_or_404(Patient, id=patient_id)
        
        # Get latest measurements
        latest_measurements = Measurements.objects.filter(patient=patient).order_by('-date').first()
        
        if latest_measurements:
            # Calculate BMI
            weight_kg = latest_measurements.weight * 0.453592  # Convert lbs to kg
            height_m = latest_measurements.height * 0.0254    # Convert inches to meters
            bmi = weight_kg / (height_m * height_m) if height_m > 0 else None
            
            data = {
                'weight': latest_measurements.weight,
                'bmi': round(bmi, 1) if bmi else None
            }
        else:
            data = {
                'weight': None,
                'bmi': None
            }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_dashboard_metrics(request, patient_id):
    """API endpoint for dashboard metrics"""
    try:
        patient = get_object_or_404(Patient, id=patient_id)
        logger.info(f"Fetching dashboard metrics for patient {patient_id}")
        
        # Get date range from request
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # Build base querysets
        visits_query = Visits.objects.filter(patient=patient)
        cmp_labs_query = CmpLabs.objects.filter(patient=patient)
        cbc_labs_query = CbcLabs.objects.filter(patient=patient)
        vitals_query = Vitals.objects.filter(patient=patient)
        measurements_query = Measurements.objects.filter(patient=patient)
        
        # Apply date filters if provided
        if start_date and end_date:
            try:
                start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
                logger.info(f"Using date range: {start_date} to {end_date}")
                
                visits_query = visits_query.filter(date__range=[start_date, end_date])
                cmp_labs_query = cmp_labs_query.filter(date__range=[start_date, end_date])
                cbc_labs_query = cbc_labs_query.filter(date__range=[start_date, end_date])
                vitals_query = vitals_query.filter(date__range=[start_date, end_date])
                measurements_query = measurements_query.filter(date__range=[start_date, end_date])
            except ValueError as e:
                logger.error(f"Invalid date format: {str(e)}")
        
        # Get latest records
        latest_vitals = vitals_query.order_by('-date').first()
        latest_cmp = cmp_labs_query.order_by('-date').first()
        latest_cbc = cbc_labs_query.order_by('-date').first()
        latest_measurements = measurements_query.order_by('-date').first()
        
        # Get metrics
        metrics = {
            'total_visits': visits_query.count(),
            'active_medications': Medications.objects.filter(
                patient=patient,
                dc_date__isnull=True
            ).count(),
            'recent_labs': cmp_labs_query.count() + cbc_labs_query.count(),
            'pending_tasks': RecordRequestLog.objects.filter(
                patient=patient,
                status='pending'
            ).count()
        }
        
        # Get latest values for display
        latest_values = {
            'bp': latest_vitals.blood_pressure if latest_vitals else '--/--',
            'hr': str(latest_vitals.pulse) if latest_vitals else '--',
            'glucose': latest_cmp.glucose if latest_cmp else None,
            'wbc': latest_cbc.wbc if latest_cbc else None,
            'weight': latest_measurements.weight if latest_measurements else None,
            'bmi': None  # Will calculate if we have height and weight
        }
        
        # Calculate BMI if we have both height and weight
        if latest_measurements and patient.height_inches:
            weight_kg = latest_measurements.weight * 0.453592  # Convert lbs to kg
            height_m = patient.height_inches * 0.0254  # Convert inches to meters
            if height_m > 0:
                latest_values['bmi'] = round(weight_kg / (height_m * height_m), 1)
        
        # Get vitals data for chart
        vitals_data = []
        for vital in vitals_query.order_by('date'):
            try:
                systolic, diastolic = map(int, vital.blood_pressure.split('/'))
                vitals_data.append({
                    'date': vital.date.isoformat(),
                    'systolic': systolic,
                    'diastolic': diastolic,
                    'heart_rate': vital.pulse
                })
            except (ValueError, AttributeError) as e:
                logger.error(f"Error parsing vital signs: {str(e)}")
                continue
        
        # Get recent activities
        activities = EventStore.objects.filter(
            aggregate_id=str(patient_id),
            event_type__in=['RECORD_CREATED', 'RECORD_UPDATED', 'STATUS_CHANGED']
        ).order_by('-timestamp')[:10]
        
        activities_data = [{
            'timestamp': activity.timestamp.isoformat(),
            'action': activity.action,
            'description': activity.record_type
        } for activity in activities]
        
        # Generate alerts
        alerts = []
        
        # Check for abnormal vitals
        if latest_vitals:
            try:
                systolic, diastolic = map(int, latest_vitals.blood_pressure.split('/'))
                
                if systolic > 180 or diastolic > 110:
                    alerts.append({
                        'severity': 'high',
                        'message': f'High blood pressure: {latest_vitals.blood_pressure}'
                    })
                elif systolic < 90 or diastolic < 60:
                    alerts.append({
                        'severity': 'high',
                        'message': f'Low blood pressure: {latest_vitals.blood_pressure}'
                    })
                    
                if latest_vitals.temperature > 38.3:  # >101°F
                    alerts.append({
                        'severity': 'high',
                        'message': f'High temperature: {latest_vitals.temperature}°C'
                    })
                    
                if latest_vitals.spo2 < 95:
                    alerts.append({
                        'severity': 'medium',
                        'message': f'Low SpO2: {latest_vitals.spo2}%'
                    })
            except (ValueError, AttributeError) as e:
                logger.error(f"Error checking vital signs alerts: {str(e)}")
        
        # Check for abnormal labs
        if latest_cbc:
            if latest_cbc.wbc > 11.0 or latest_cbc.wbc < 4.0:
                alerts.append({
                    'severity': 'medium',
                    'message': f'Abnormal WBC: {latest_cbc.wbc} K/µL'
                })
        
        if latest_cmp:
            if latest_cmp.glucose > 200:
                alerts.append({
                    'severity': 'medium',
                    'message': f'High glucose: {latest_cmp.glucose} mg/dL'
                })
        
        response_data = {
            'success': True,
            'metrics': metrics,
            'latest_values': latest_values,
            'vitals_data': vitals_data,
            'activities': activities_data,
            'alerts': alerts
        }
        
        logger.info(f"Successfully fetched dashboard data for patient {patient_id}")
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error fetching dashboard metrics: {str(e)}", exc_info=True)
        return JsonResponse({
            'error': str(e),
            'success': False
        }, status=500)

@login_required
def patient_section_data(request, patient_id, section):
    """Load a specific section of patient data."""
    patient = get_object_or_404(Patient, id=patient_id)
    template_name = f'patient_records/partials/_{section}.html'
    
    context = {
        'patient': patient,
    }
    
    # Add section-specific data
    if section == 'visits':
        context['visits'] = patient.visit_set.all().order_by('-visit_date')
    elif section == 'medications':
        context['medications'] = patient.medication_set.all().order_by('-start_date')
    elif section == 'vitals':
        context['vitals'] = patient.vitalsigns_set.all().order_by('-recorded_at')[:10]
    elif section == 'diagnoses':
        context['diagnoses'] = patient.diagnosis_set.all().order_by('-diagnosed_date')
    elif section == 'labs':
        context['cmp_labs'] = patient.cmplabs_set.all().order_by('-recorded_at')[:5]
        context['cbc_labs'] = patient.cbclabs_set.all().order_by('-recorded_at')[:5]
    
    return render(request, template_name, context)

@login_required
def vitals_list(request, patient_id):
    """View list of vitals records for a patient."""
    patient = get_object_or_404(Patient, id=patient_id)
    vitals = Vitals.objects.filter(patient=patient).order_by('-date')
    
    context = {
        'patient': patient,
        'vitals': vitals,
        'breadcrumbs': [
            {'label': 'Patients', 'url': reverse('patient_list')},
            {'label': f'Patient {patient.id}', 'url': reverse('patient_detail', args=[patient.id])},
            {'label': 'Vitals History', 'url': None}
        ]
    }
    return render(request, 'patient_records/vitals_list.html', context)

@login_required
def medications_list(request, patient_id):
    """View list of medications for a patient."""
    patient = get_object_or_404(Patient, id=patient_id)
    medications = Medications.objects.filter(patient=patient).order_by('-date_prescribed')
    
    context = {
        'patient': patient,
        'medications': medications,
        'breadcrumbs': [
            {'label': 'Patients', 'url': reverse('patient_list')},
            {'label': f'Patient {patient.id}', 'url': reverse('patient_detail', args=[patient.id])},
            {'label': 'Medications History', 'url': None}
        ]
    }
    return render(request, 'patient_records/medications_list.html', context)

@login_required
def diagnoses_list(request, patient_id):
    """View list of diagnoses for a patient."""
    patient = get_object_or_404(Patient, id=patient_id)
    diagnoses = Diagnosis.objects.filter(patient=patient).order_by('-date')
    
    context = {
        'patient': patient,
        'diagnoses': diagnoses,
        'breadcrumbs': [
            {'label': 'Patients', 'url': reverse('patient_list')},
            {'label': f'Patient {patient.id}', 'url': reverse('patient_detail', args=[patient.id])},
            {'label': 'Diagnoses History', 'url': None}
        ]
    }
    return render(request, 'patient_records/diagnoses_list.html', context)

@login_required
def cbc_labs_list(request, patient_id):
    """View list of CBC lab results for a patient."""
    patient = get_object_or_404(Patient, id=patient_id)
    labs = CbcLabs.objects.filter(patient=patient).order_by('-date')
    
    context = {
        'patient': patient,
        'labs': labs,
        'breadcrumbs': [
            {'label': 'Patients', 'url': reverse('patient_list')},
            {'label': f'Patient {patient.id}', 'url': reverse('patient_detail', args=[patient.id])},
            {'label': 'CBC Labs History', 'url': None}
        ]
    }
    return render(request, 'patient_records/cbc_labs_list.html', context)

@login_required
def cmp_labs_list(request, patient_id):
    """View list of CMP lab results for a patient."""
    patient = get_object_or_404(Patient, id=patient_id)
    labs = CmpLabs.objects.filter(patient=patient).order_by('-date')
    
    context = {
        'patient': patient,
        'labs': labs,
        'breadcrumbs': [
            {'label': 'Patients', 'url': reverse('patient_list')},
            {'label': f'Patient {patient.id}', 'url': reverse('patient_detail', args=[patient.id])},
            {'label': 'CMP Labs History', 'url': None}
        ]
    }
    return render(request, 'patient_records/cmp_labs_list.html', context)

@login_required
def symptoms_list(request, patient_id):
    """View list of symptoms for a patient."""
    patient = get_object_or_404(Patient, id=patient_id)
    symptoms = Symptoms.objects.filter(patient=patient).order_by('-date')
    
    context = {
        'patient': patient,
        'symptoms': symptoms,
        'breadcrumbs': [
            {'label': 'Patients', 'url': reverse('patient_list')},
            {'label': f'Patient {patient.id}', 'url': reverse('patient_detail', args=[patient.id])},
            {'label': 'Symptoms History', 'url': None}
        ]
    }
    return render(request, 'patient_records/symptoms_list.html', context)

@login_required
def visits_list(request, patient_id):
    """View list of visits for a patient."""
    patient = get_object_or_404(Patient, id=patient_id)
    visits = Visits.objects.filter(patient=patient).order_by('-date')
    
    context = {
        'patient': patient,
        'visits': visits,
        'breadcrumbs': [
            {'label': 'Patients', 'url': reverse('patient_list')},
            {'label': f'Patient {patient.id}', 'url': reverse('patient_detail', args=[patient.id])},
            {'label': 'Visits History', 'url': None}
        ]
    }
    return render(request, 'patient_records/visits_list.html', context)

@login_required
def measurements_list(request, patient_id):
    """View list of measurements for a patient."""
    patient = get_object_or_404(Patient, id=patient_id)
    measurements = Measurements.objects.filter(patient=patient).order_by('-date')
    
    context = {
        'patient': patient,
        'measurements': measurements,
        'breadcrumbs': [
            {'label': 'Patients', 'url': reverse('patient_list')},
            {'label': f'Patient {patient.id}', 'url': reverse('patient_detail', args=[patient.id])},
            {'label': 'Measurements History', 'url': None}
        ]
    }
    return render(request, 'patient_records/measurements_list.html', context)

@login_required
def adls_list(request, patient_id):
    """View list of ADLs for a patient."""
    patient = get_object_or_404(Patient, id=patient_id)
    adls = Adls.objects.filter(patient=patient).order_by('-date')
    
    context = {
        'patient': patient,
        'adls': adls,
        'breadcrumbs': [
            {'label': 'Patients', 'url': reverse('patient_list')},
            {'label': f'Patient {patient.id}', 'url': reverse('patient_detail', args=[patient.id])},
            {'label': 'ADLs History', 'url': None}
        ]
    }
    return render(request, 'patient_records/adls_list.html', context)

@login_required
def imaging_list(request, patient_id):
    """View list of imaging studies for a patient."""
    patient = get_object_or_404(Patient, id=patient_id)
    imaging = Imaging.objects.filter(patient=patient).order_by('-date')
    
    context = {
        'patient': patient,
        'imaging': imaging,
        'breadcrumbs': [
            {'label': 'Patients', 'url': reverse('patient_list')},
            {'label': f'Patient {patient.id}', 'url': reverse('patient_detail', args=[patient.id])},
            {'label': 'Imaging History', 'url': None}
        ]
    }
    return render(request, 'patient_records/imaging_list.html', context)

@login_required
def occurrences_list(request, patient_id):
    """View list of occurrences for a patient."""
    patient = get_object_or_404(Patient, id=patient_id)
    occurrences = Occurrences.objects.filter(patient=patient).order_by('-date')
    
    context = {
        'patient': patient,
        'occurrences': occurrences,
        'breadcrumbs': [
            {'label': 'Patients', 'url': reverse('patient_list')},
            {'label': f'Patient {patient.id}', 'url': reverse('patient_detail', args=[patient.id])},
            {'label': 'Occurrences History', 'url': None}
        ]
    }
    return render(request, 'patient_records/occurrences_list.html', context)

@login_required
def record_requests_list(request, patient_id):
    """View list of record requests for a patient."""
    patient = get_object_or_404(Patient, id=patient_id)
    requests = RecordRequestLog.objects.filter(patient=patient).order_by('-date')
    
    context = {
        'patient': patient,
        'requests': requests,
        'breadcrumbs': [
            {'label': 'Patients', 'url': reverse('patient_list')},
            {'label': f'Patient {patient.id}', 'url': reverse('patient_detail', args=[patient.id])},
            {'label': 'Record Requests History', 'url': None}
        ]
    }
    return render(request, 'patient_records/record_requests_list.html', context)

@login_required
def record_detail(request, record_type, record_id):
    """Display detailed view of a specific record."""
    # Map record types to their corresponding models
    record_models = {
        'vitals': Vitals,
        'medications': Medications,
        'diagnosis': Diagnosis,
        'cbc_labs': CbcLabs,
        'cmp_labs': CmpLabs,
        'symptoms': Symptoms,
        'visits': Visits,
        'measurements': Measurements,
        'adls': Adls,
        'imaging': Imaging,
        'occurrences': Occurrences,
        'record_requests': RecordRequestLog
    }
    
    # Get the appropriate model for the record type
    model = record_models.get(record_type.lower())
    if not model:
        messages.error(request, f'Invalid record type: {record_type}')
        return redirect('home')
    
    # Get the record instance
    record = get_object_or_404(model, id=record_id)
    
    # Ensure user has access to this patient's records
    if not request.user.is_staff and record.patient.primary_provider != request.user:
        messages.error(request, 'You do not have permission to view this record')
        return redirect('home')
    
    # Convert record to dictionary for template
    record_data = serialize_model_instance(record)
    
    # Get audit trail for this record
    audit_trail = AuditTrail.objects.filter(
        record_type=record_type.upper(),
        record_id=str(record_id)
    ).order_by('-created_at')
    
    context = {
        'record': record,
        'record_data': record_data,
        'record_type': record_type,
        'audit_trail': audit_trail,
        'patient': record.patient
    }
    
    return render(request, 'patient_records/record_detail.html', context)
