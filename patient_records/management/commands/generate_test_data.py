"""Command to generate test data for the patient management system."""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from contextlib import contextmanager
from patient_records.models import (
    Patient, Medications, CbcLabs, CmpLabs, 
    Symptoms, Diagnosis, Visits, Provider,
    Measurements, Imaging, Adls, Occurrences,
    ClinicalNote, PatientNote, NoteTag, NoteAttachment,
    Vitals, EventStore, AuditTrail, RecordRequestLog
)
from patient_records.models.audit.constants import (
    PATIENT_AGGREGATE, CLINICAL_AGGREGATE,
    PATIENT_REGISTERED, PATIENT_UPDATED,
    VITALS_RECORDED, LAB_RESULTS_ADDED,
    SYMPTOMS_ADDED, DIAGNOSIS_ADDED,
    VISIT_RECORDED, MEASUREMENT_RECORDED,
    IMAGING_ADDED, ADLS_RECORDED,
    OCCURRENCE_RECORDED, NOTE_CREATED,
    MEDICATION_ADDED
)
import datetime
from decimal import Decimal
import random
import uuid
from faker import Faker
from django.utils import timezone

fake = Faker()

@contextmanager
def disable_event_creation():
    """Temporarily disable event creation in models."""
    from patient_records.models.base import BasePatientModel
    original_save = BasePatientModel.save
    
    def new_save(self, *args, **kwargs):
        kwargs['no_events'] = True
        return original_save(self, *args, **kwargs)
    
    BasePatientModel.save = new_save
    try:
        yield
    finally:
        BasePatientModel.save = original_save

class Command(BaseCommand):
    """Generate test data for the patient management system."""
    
    help = 'Generates test data for the patient management system'

    def __init__(self):
        """Initialize command."""
        super().__init__()
        self.fake = Faker()
        self.record_count = 100
        self.providers = []
        self.patients = []
        self.sequence_counters = {}  # Track event sequences per aggregate
        
    def handle(self, *args, **kwargs):
        """Execute the command."""
        self.stdout.write('Generating test data...')
        
        # Create test user if doesn't exist
        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'is_staff': True
            }
        )
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            self.stdout.write(f'Created test user: testuser/testpass123')

        # Create providers first (needed for visits)
        self.stdout.write('Creating providers...')
        self._create_providers()
        
        # Create note tags (needed for patient notes)
        self.stdout.write('Creating note tags...')
        self._create_note_tags()
        
        # Create test patients and their related records
        self.stdout.write('Creating patients and their records...')
        self._create_patients()
        
        total = len(self.patients)
        with disable_event_creation():
            for i, patient in enumerate(self.patients, 1):
                self._create_medications(patient)
                self._create_cbc_labs(patient)
                self._create_cmp_labs(patient)
                self._create_symptoms(patient)
                self._create_diagnosis(patient)
                self._create_visits(patient)
                self._create_measurements(patient)
                self._create_imaging(patient)
                self._create_adls(patient)
                self._create_occurrences(patient)
                self._create_clinical_notes(patient)
                self._create_patient_notes(patient)
                self._create_vitals(patient)
                self._create_audit_trail(patient)
                self._create_record_request_logs(patient)
                
                if i % 10 == 0:
                    self.stdout.write(f'Processed {i}/{total} patients')
            
        self.stdout.write(self.style.SUCCESS('Successfully generated test data'))

    def _get_next_sequence(self, aggregate_type, aggregate_id):
        """Get next sequence number for an aggregate."""
        key = f"{aggregate_type}:{aggregate_id}"
        if key not in self.sequence_counters:
            # Check if there are any existing events for this aggregate
            last_sequence = EventStore.objects.filter(
                aggregate_type=aggregate_type,
                aggregate_id=str(aggregate_id)
            ).order_by('-sequence').values_list('sequence', flat=True).first()
            
            self.sequence_counters[key] = last_sequence or 0
            
        self.sequence_counters[key] += 1
        return self.sequence_counters[key]

    def _create_event(self, aggregate_type, aggregate_id, event_type, event_data):
        """Create an event in the event store."""
        sequence = self._get_next_sequence(aggregate_type, aggregate_id)
        EventStore.objects.create(
            aggregate_type=aggregate_type,
            aggregate_id=str(aggregate_id),
            event_type=event_type,
            event_data=event_data,
            sequence=sequence
        )

    def _create_providers(self):
        """Create test providers."""
        for _ in range(5):
            provider = Provider.objects.create(
                provider=fake.name(),
                practice=fake.company(),
                address=fake.street_address(),
                city=fake.city(),
                state=fake.state_abbr(),
                zip_code=fake.zipcode(),
                phone=f"{fake.msisdn()[:3]}-{fake.msisdn()[3:6]}-{fake.msisdn()[6:10]}",
                fax=f"{fake.msisdn()[:3]}-{fake.msisdn()[3:6]}-{fake.msisdn()[6:10]}",
                is_active=True,
                registration_date=timezone.now().date()
            )
            self.providers.append(provider)

    def _create_patients(self):
        """Create test patients."""
        for _ in range(self.record_count):
            patient = Patient.objects.create(
                patient_number=f"P{self.fake.unique.random_number(digits=6)}",
                first_name=self.fake.first_name()[:100],
                middle_name=self.fake.first_name()[:100] if random.choice([True, False]) else None,
                last_name=self.fake.last_name()[:100],
                date_of_birth=self.fake.date_of_birth(),
                gender=random.choice(['M', 'F', 'O', 'N']),
                address=f"{self.fake.street_address()}\n{self.fake.city()}, {self.fake.state()} {self.fake.zipcode()}",
                phone=self.fake.phone_number()[:20],
                email=self.fake.email(),
                emergency_contact=f"Name: {self.fake.name()}\nRelation: {random.choice(['Spouse', 'Child', 'Parent', 'Sibling'])}\nPhone: {self.fake.phone_number()}",
                insurance_info=f"Provider: {self.fake.company()}\nPolicy #: {self.fake.random_number(digits=8)}\nGroup #: {self.fake.random_number(digits=6)}",
                primary_provider=random.choice(self.providers)
            )
            self.patients.append(patient)
            
            # Create patient registration event
            self._create_event(
                PATIENT_AGGREGATE,
                patient.id,
                PATIENT_REGISTERED,
                {
                    'patient_id': str(patient.id),
                    'patient_number': patient.patient_number,
                    'name': f"{patient.first_name} {patient.last_name}",
                    'date_of_birth': patient.date_of_birth.isoformat(),
                    'gender': patient.gender
                }
            )

    def _create_medications(self, patient):
        """Create test medications for a patient."""
        medications = [
            ('Lisinopril', '10mg', 'PO', 'Once daily'),
            ('Metformin', '500mg', 'PO', 'Twice daily'),
            ('Aspirin', '81mg', 'PO', 'Once daily'),
            ('Insulin', '10 units', 'SC', 'Before meals'),
            ('Albuterol', '2 puffs', 'INH', 'Every 4-6 hours as needed'),
            ('Fentanyl', '25mcg', 'TD', 'Every 72 hours'),
            ('Morphine', '2mg', 'IV', 'Every 4 hours as needed'),
            ('Ceftriaxone', '1g', 'IM', 'Every 24 hours'),
            ('Nitroglycerin', '0.4mg', 'SL', 'As needed for chest pain'),
            ('Hydrocortisone', '1%', 'TOP', 'Twice daily')
        ]
        
        for _ in range(random.randint(2, 5)):
            date = self.fake_date_within_year()
            prescribed_date = date
            
            # 25% chance of medication being discontinued
            dc_date = None
            if random.random() < 0.25:
                dc_date = date + datetime.timedelta(days=random.randint(30, 180))
            
            med = random.choice(medications)
            medication = Medications.objects.create(
                patient=patient,
                date=date,
                drug=med[0],
                dose=med[1],
                route=med[2],  # These now match the ROUTE_CHOICES in the model
                frequency=med[3],
                date_prescribed=prescribed_date,
                dc_date=dc_date,
                notes=fake.text(max_nb_chars=200),
                prn=random.choice([True, False]),
                provider=random.choice(self.providers)
            )
            
            # Create medication event
            self._create_event(
                CLINICAL_AGGREGATE,
                patient.id,
                MEDICATION_ADDED,
                {
                    'medication_id': str(medication.id),
                    'date': medication.date.isoformat(),
                    'drug': medication.drug,
                    'dose': medication.dose,
                    'route': medication.route,
                    'frequency': medication.frequency,
                    'date_prescribed': medication.date_prescribed.isoformat(),
                    'dc_date': medication.dc_date.isoformat() if medication.dc_date else None,
                    'notes': medication.notes,
                    'prn': medication.prn,
                    'provider': str(medication.provider.id) if medication.provider else None
                }
            )

    def _create_cbc_labs(self, patient):
        """Create test CBC labs for a patient."""
        for _ in range(random.randint(2, 5)):
            date = self.fake_date_within_year()
            labs = CbcLabs.objects.create(
                patient=patient,
                date=date,
                rbc=round(random.uniform(4.0, 6.0), 2),
                wbc=round(random.uniform(4.0, 11.0), 2),
                hemoglobin=round(random.uniform(12.0, 17.0), 2),
                hematocrit=round(random.uniform(35.0, 50.0), 2),
                mcv=round(random.uniform(80.0, 100.0), 2),
                mchc=round(random.uniform(31.0, 37.0), 2),
                rdw=round(random.uniform(11.5, 14.5), 2),
                platelets=round(random.uniform(150.0, 450.0), 2),
                mch=round(random.uniform(27.0, 32.0), 2),
                neutrophils=round(random.uniform(40.0, 70.0), 2),
                lymphocytes=round(random.uniform(20.0, 40.0), 2),
                monocytes=round(random.uniform(2.0, 8.0), 2),
                eosinophils=round(random.uniform(1.0, 4.0), 2),
                basophils=round(random.uniform(0.5, 1.0), 2)
            )
            
            # Create lab results event
            self._create_event(
                CLINICAL_AGGREGATE,
                patient.id,
                LAB_RESULTS_ADDED,
                {
                    'lab_id': str(labs.id),
                    'type': 'CBC',
                    'date': labs.date.isoformat(),
                    'rbc': float(labs.rbc),
                    'wbc': float(labs.wbc),
                    'hemoglobin': float(labs.hemoglobin),
                    'hematocrit': float(labs.hematocrit),
                    'mcv': float(labs.mcv),
                    'mchc': float(labs.mchc),
                    'rdw': float(labs.rdw),
                    'platelets': float(labs.platelets),
                    'mch': float(labs.mch),
                    'neutrophils': float(labs.neutrophils),
                    'lymphocytes': float(labs.lymphocytes),
                    'monocytes': float(labs.monocytes),
                    'eosinophils': float(labs.eosinophils),
                    'basophils': float(labs.basophils)
                }
            )

    def _create_cmp_labs(self, patient):
        """Create test CMP labs for a patient."""
        for _ in range(random.randint(2, 5)):
            date = self.fake_date_within_year()
            labs = CmpLabs.objects.create(
                patient=patient,
                date=date,
                sodium=round(random.uniform(135.0, 145.0), 2),
                potassium=round(random.uniform(3.5, 5.0), 2),
                chloride=round(random.uniform(96.0, 106.0), 2),
                co2=round(random.uniform(23.0, 29.0), 2),
                glucose=round(random.uniform(70.0, 100.0), 2),
                bun=round(random.uniform(7.0, 20.0), 2),
                creatinine=round(random.uniform(0.6, 1.2), 2),
                calcium=round(random.uniform(8.5, 10.5), 2),
                protein=round(random.uniform(6.0, 8.0), 2),
                albumin=round(random.uniform(3.5, 5.0), 2),
                bilirubin=round(random.uniform(0.3, 1.2), 2),
                gfr=round(random.uniform(90.0, 120.0), 2)
            )
            
            # Create lab results event
            self._create_event(
                CLINICAL_AGGREGATE,
                patient.id,
                LAB_RESULTS_ADDED,
                {
                    'lab_id': str(labs.id),
                    'type': 'CMP',
                    'date': labs.date.isoformat(),
                    'sodium': float(labs.sodium),
                    'potassium': float(labs.potassium),
                    'chloride': float(labs.chloride),
                    'co2': float(labs.co2),
                    'glucose': float(labs.glucose),
                    'bun': float(labs.bun),
                    'creatinine': float(labs.creatinine),
                    'calcium': float(labs.calcium),
                    'protein': float(labs.protein),
                    'albumin': float(labs.albumin),
                    'bilirubin': float(labs.bilirubin),
                    'gfr': float(labs.gfr)
                }
            )

    def _create_symptoms(self, patient):
        """Create test symptoms for a patient."""
        symptoms_list = [
            'Fatigue', 'Headache', 'Nausea', 'Dizziness', 'Cough',
            'Fever', 'Joint Pain', 'Muscle Aches', 'Shortness of Breath'
        ]
        
        for _ in range(random.randint(2, 5)):
            date = self.fake_date_within_year()
            
            # Create symptom - the model will handle event creation
            Symptoms.objects.create(
                patient=patient,
                date=date,
                symptom=random.choice(symptoms_list),
                severity=random.randint(1, 5),
                notes=fake.text(max_nb_chars=200),
                person_reporting=random.choice(['Patient', 'Family Member', 'Caregiver']),
                provider=random.choice(self.providers)
            )

    def _create_diagnosis(self, patient):
        """Create test diagnoses for a patient."""
        diagnoses = [
            ('E11.9', 'Type 2 diabetes mellitus without complications'),
            ('I10', 'Essential (primary) hypertension'),
            ('J45.909', 'Unspecified asthma, uncomplicated'),
            ('M17.0', 'Bilateral primary osteoarthritis of knee'),
            ('F41.1', 'Generalized anxiety disorder')
        ]
        
        for _ in range(random.randint(1, 3)):
            date = self.fake_date_within_year()
            icd_code, diagnosis_text = random.choice(diagnoses)
            is_active = random.choice([True, True, False])  # Bias towards active
            resolved_date = None
            if not is_active:
                resolved_date = date + datetime.timedelta(days=random.randint(30, 180))
            
            diagnosis = Diagnosis.objects.create(
                patient=patient,
                date=date,
                icd_code=icd_code,
                diagnosis=diagnosis_text,
                provider=random.choice(self.providers),
                notes=fake.text(max_nb_chars=200),
                is_active=is_active,
                resolved_date=resolved_date
            )
            
            # Create diagnosis event
            self._create_event(
                CLINICAL_AGGREGATE,
                patient.id,
                DIAGNOSIS_ADDED,
                {
                    'diagnosis_id': str(diagnosis.id),
                    'date': diagnosis.date.isoformat(),
                    'icd_code': diagnosis.icd_code,
                    'diagnosis': diagnosis.diagnosis,
                    'is_active': diagnosis.is_active,
                    'resolved_date': diagnosis.resolved_date.isoformat() if diagnosis.resolved_date else None
                }
            )

    def _create_visits(self, patient):
        """Create test visits for a patient."""
        for _ in range(random.randint(2, 6)):
            date = self.fake_date_within_year()
            visit = Visits.objects.create(
                patient=patient,
                date=date,
                visit_type=random.choice(['OFFICE', 'HOME', 'VIRTUAL', 'HOSPITAL', 'EMERGENCY', 'FOLLOWUP']),
                provider=random.choice(self.providers),
                practice=fake.company(),
                chief_complaint=fake.text(max_nb_chars=100),
                notes=fake.text(max_nb_chars=200),
                follow_up_needed=random.choice([True, False])
            )
            
            if visit.follow_up_needed:
                visit.follow_up_date = date + datetime.timedelta(days=random.randint(7, 30))
                visit.save()
            
            # Create visit event
            self._create_event(
                CLINICAL_AGGREGATE,
                patient.id,
                VISIT_RECORDED,
                {
                    'visit_id': str(visit.id),
                    'date': visit.date.isoformat(),
                    'visit_type': visit.visit_type,
                    'provider': str(visit.provider.id) if visit.provider else None,
                    'practice': visit.practice,
                    'chief_complaint': visit.chief_complaint,
                    'follow_up_needed': visit.follow_up_needed,
                    'follow_up_date': visit.follow_up_date.isoformat() if visit.follow_up_date else None
                }
            )

    def _create_measurements(self, patient):
        """Create test measurements for a patient."""
        for _ in range(random.randint(2, 4)):
            date = self.fake_date_within_year()
            measurements = Measurements.objects.create(
                patient=patient,
                date=date,
                weight=round(random.uniform(100.0, 250.0), 1),
                value=round(random.uniform(1.0, 100.0), 1) if random.choice([True, False]) else None,
                nutritional_intake=random.choice(['Good', 'Fair', 'Poor']),
                mac=f"{random.randint(20, 35)} cm",
                fast=str(random.randint(0, 5)),
                pps=f"{random.randint(40, 100)}%",
                plof=random.choice(['Independent', 'Modified Independent', 'Supervision', 'Minimal Assist'])
            )
            
            # Create measurement event
            self._create_event(
                CLINICAL_AGGREGATE,
                patient.id,
                MEASUREMENT_RECORDED,
                {
                    'measurement_id': str(measurements.id),
                    'date': measurements.date.isoformat(),
                    'weight': measurements.weight,
                    'value': measurements.value,
                    'nutritional_intake': measurements.nutritional_intake,
                    'mac': measurements.mac,
                    'fast': measurements.fast,
                    'pps': measurements.pps,
                    'plof': measurements.plof
                }
            )

    def _create_clinical_notes(self, patient):
        """Create test clinical notes for a patient."""
        sources = ['EHR', 'manual', 'imported', 'transcribed']
        
        for _ in range(random.randint(3, 8)):
            date = self.fake_date_within_year()
            note = ClinicalNote.objects.create(
                patient=patient,
                date=date,
                provider=random.choice(self.providers),
                content=fake.text(max_nb_chars=500),
                source=random.choice(sources)
            )
            
            # Create note event
            self._create_event(
                CLINICAL_AGGREGATE,
                patient.id,
                NOTE_CREATED,
                {
                    'note_id': str(note.id),
                    'date': note.date.isoformat(),
                    'provider': str(note.provider.id) if note.provider else None,
                    'content': note.content,
                    'source': note.source
                }
            )

    def _create_note_tags(self):
        """Create common note tags."""
        tags = [
            ('Clinical', 'Clinical observations and findings'),
            ('Follow-up', 'Follow-up items and reminders'),
            ('Urgent', 'Urgent or important notes'),
            ('Care Plan', 'Care plan related notes'),
            ('Family', 'Family communication notes'),
            ('Medication', 'Medication related notes'),
            ('Lab Results', 'Laboratory results notes'),
            ('Progress', 'Progress notes'),
        ]
        
        for name, description in tags:
            NoteTag.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )

    def _create_patient_notes(self, patient):
        """Create test patient notes for a patient."""
        # Get all available tags
        tags = list(NoteTag.objects.all())
        
        # Get content types for different record types
        visit_ct = ContentType.objects.get_for_model(Visits)
        lab_ct = ContentType.objects.get_for_model(CmpLabs)
        medication_ct = ContentType.objects.get_for_model(Medications)
        
        # Get some random records to reference
        visits = list(Visits.objects.filter(patient=patient))
        labs = list(CmpLabs.objects.filter(patient=patient))
        medications = list(Medications.objects.filter(patient=patient))
        
        for _ in range(random.randint(5, 12)):
            date = self.fake_date_within_year()
            
            # Randomly decide if this note should reference a record
            referenced_record = None
            content_type = None
            object_id = None
            
            if random.choice([True, False]) and (visits or labs or medications):
                record_type = random.choice(['visit', 'lab', 'medication'])
                if record_type == 'visit' and visits:
                    referenced_record = random.choice(visits)
                    content_type = visit_ct
                    object_id = referenced_record.id
                elif record_type == 'lab' and labs:
                    referenced_record = random.choice(labs)
                    content_type = lab_ct
                    object_id = referenced_record.id
                elif record_type == 'medication' and medications:
                    referenced_record = random.choice(medications)
                    content_type = medication_ct
                    object_id = referenced_record.id
            
            note = PatientNote.objects.create(
                patient=patient,
                date=date,
                title=fake.sentence()[:200],
                content=fake.text(max_nb_chars=500),
                category=random.choice(['OVERVIEW', 'CLINICAL', 'VISITS', 'MEDICATIONS', 'LABS', 'VITALS', 'GENERAL']),
                created_by=User.objects.first(),  # Using the test user
                is_pinned=random.choice([True, False, False, False]),  # 25% chance of being pinned
                content_type=content_type,
                object_id=object_id
            )
            
            # Add random tags (1-3 tags per note)
            note.tags.add(*random.sample(tags, random.randint(1, min(3, len(tags)))))
            
            # Maybe add an attachment (30% chance)
            if random.random() < 0.3:
                self._create_note_attachment(note)
            
            # Create note event
            self._create_event(
                CLINICAL_AGGREGATE,
                patient.id,
                NOTE_CREATED,
                {
                    'note_id': str(note.id),
                    'date': note.date.isoformat(),
                    'title': note.title,
                    'content': note.content,
                    'category': note.category,
                    'created_by': str(note.created_by.id) if note.created_by else None,
                    'is_pinned': note.is_pinned,
                    'content_type': note.content_type.model if note.content_type else None,
                    'object_id': str(note.object_id) if note.object_id else None,
                    'tags': [tag.name for tag in note.tags.all()]
                }
            )

    def _create_note_attachment(self, note):
        """Create a test attachment for a note."""
        file_types = ['pdf', 'jpg', 'png', 'doc']
        file_type = random.choice(file_types)
        
        # Create a dummy file content
        content = ContentFile(b'Test file content', name=f'test_file.{file_type}')
        
        # Create the attachment
        attachment = NoteAttachment.objects.create(
            note=note,
            file=content,
            filename=f'test_file.{file_type}',
            file_type=file_type
        )

    def _create_audit_trail(self, patient):
        """Create audit trail entries for a patient."""
        actions = [
            'CREATE', 'UPDATE', 'DELETE'
        ]
        
        record_types = [
            'Patient', 'ClinicalNote', 'LabResult',
            'Medication', 'Vital', 'Visit', 'Imaging'
        ]
        
        for _ in range(random.randint(10, 20)):
            action = random.choice(actions)
            record_type = random.choice(record_types)
            
            # Create some sample data for the audit
            if action == 'CREATE':
                previous_values = {}
                new_values = {
                    'created_at': timezone.now().isoformat(),
                    'details': fake.sentence()
                }
            elif action == 'UPDATE':
                previous_values = {
                    'field1': fake.word(),
                    'field2': fake.word()
                }
                new_values = {
                    'field1': fake.word(),
                    'field2': fake.word()
                }
            else:  # DELETE
                previous_values = {
                    'record_id': str(uuid.uuid4()),
                    'details': fake.sentence()
                }
                new_values = {}
            
            AuditTrail.objects.create(
                patient=patient,
                patient_identifier=f"{patient.first_name} {patient.last_name} ({patient.patient_number})",
                action=action,
                record_type=record_type,
                user=User.objects.first(),  # Using test user
                previous_values=previous_values,
                new_values=new_values
            )

    def _create_record_request_logs(self, patient):
        """Create record request logs for a patient."""
        request_types = [
            'Medical Records', 'Lab Results', 'Imaging Results',
            'Visit Summary', 'Complete History'
        ]
        
        requesters = [
            'Patient', 'Family Member', 'Provider',
            'Insurance Company', 'Legal Representative'
        ]

        organizations = [
            'Memorial Hospital', 'Sunshine Medical Group',
            'ABC Insurance', 'XYZ Law Firm', 'State Medical Board'
        ]
        
        status_choices = [
            'PENDING', 'APPROVED', 'COMPLETED',
            'DENIED', 'CANCELLED'
        ]
        
        for _ in range(random.randint(2, 5)):
            date = self.fake_date_within_year()
            
            # For completed requests, add completion date
            status = random.choice(status_choices)
            due_date = date + datetime.timedelta(days=random.randint(1, 14))
            
            # Set needs_attention for urgent requests
            needs_attention = status in ['PENDING'] and random.random() < 0.3
            
            RecordRequestLog.objects.create(
                patient=patient,
                date=date,
                request_type=random.choice(request_types),
                requester_name=random.choice(requesters),
                requester_organization=random.choice(organizations),
                purpose=fake.sentence(),
                records_requested=fake.text(max_nb_chars=200),
                due_date=due_date,
                status=status,
                notes=fake.text(max_nb_chars=300) if random.random() < 0.7 else '',
                needs_attention=needs_attention
            )

    def _create_vitals(self, patient):
        """Create test vitals for a patient."""
        for _ in range(random.randint(3, 8)):
            date = self.fake_date_within_year()
            vitals = Vitals.objects.create(
                patient=patient,
                date=date,
                blood_pressure=f"{random.randint(100, 160)}/{random.randint(60, 100)}",
                temperature=round(random.uniform(97.0, 99.9), 1),
                spo2=random.randint(95, 100),
                pulse=random.randint(60, 100),
                respirations=random.randint(12, 20),
                supp_o2=random.choice([True, False]),
                pain=random.randint(0, 10)
            )
            
            # Create vitals recorded event
            self._create_event(
                CLINICAL_AGGREGATE,
                patient.id,
                VITALS_RECORDED,
                {
                    'vitals_id': str(vitals.id),
                    'date': vitals.date.isoformat(),
                    'blood_pressure': vitals.blood_pressure,
                    'temperature': vitals.temperature,
                    'spo2': vitals.spo2,
                    'pulse': vitals.pulse,
                    'respirations': vitals.respirations,
                    'supp_o2': vitals.supp_o2,
                    'pain': vitals.pain
                }
            )

    def _create_imaging(self, patient):
        """Create test imaging studies for a patient."""
        imaging_types = ['X-Ray', 'CT', 'MRI', 'Ultrasound', 'PET']
        body_parts = ['Chest', 'Abdomen', 'Head', 'Spine', 'Knee', 'Hip', 'Shoulder']
        
        for _ in range(random.randint(1, 3)):
            date = self.fake_date_within_year()
            imaging = Imaging.objects.create(
                patient=patient,
                date=date,
                type=random.choice(imaging_types),
                body_part=random.choice(body_parts),
                findings=fake.text(max_nb_chars=300),
                notes=fake.text(max_nb_chars=200)
            )
            
            # Create imaging event
            self._create_event(
                CLINICAL_AGGREGATE,
                patient.id,
                IMAGING_ADDED,
                {
                    'imaging_id': str(imaging.id),
                    'date': imaging.date.isoformat(),
                    'type': imaging.type,
                    'body_part': imaging.body_part,
                    'findings': imaging.findings,
                    'notes': imaging.notes
                }
            )

    def _create_adls(self, patient):
        """Create test ADL assessments for a patient."""
        status_choices = ['Independent', 'Modified Independent', 'Supervision', 'Minimal Assist', 'Moderate Assist']
        
        for _ in range(random.randint(2, 4)):
            date = self.fake_date_within_year()
            adls = Adls.objects.create(
                patient=patient,
                date=date,
                ambulation=random.choice(status_choices),
                continence=random.choice(status_choices),
                transfer=random.choice(status_choices),
                toileting=random.choice(status_choices),
                transferring=random.choice(status_choices),
                dressing=random.choice(status_choices),
                feeding=random.choice(status_choices),
                bathing=random.choice(status_choices),
                notes=fake.text(max_nb_chars=200)
            )
            
            # Create ADLs event
            self._create_event(
                CLINICAL_AGGREGATE,
                patient.id,
                ADLS_RECORDED,
                {
                    'adls_id': str(adls.id),
                    'date': adls.date.isoformat(),
                    'ambulation': adls.ambulation,
                    'continence': adls.continence,
                    'transfer': adls.transfer,
                    'toileting': adls.toileting,
                    'transferring': adls.transferring,
                    'dressing': adls.dressing,
                    'feeding': adls.feeding,
                    'bathing': adls.bathing,
                    'notes': adls.notes
                }
            )

    def _create_occurrences(self, patient):
        """Create test occurrences for a patient."""
        occurrence_types = [
            'Fall', 'Medication Error', 'Skin Breakdown', 'Behavioral Issue',
            'Pain Episode', 'Acute Illness', 'Equipment Malfunction'
        ]
        actions = [
            'Notified physician',
            'Initiated protocol',
            'Increased monitoring',
            'Provided intervention',
            'Updated care plan',
            'Family notification',
            'Emergency response activated'
        ]
        
        for _ in range(random.randint(1, 3)):
            date = self.fake_date_within_year()
            occurrence = Occurrences.objects.create(
                patient=patient,
                date=date,
                occurrence_type=random.choice(occurrence_types),
                description=fake.text(max_nb_chars=300),
                action_taken=random.choice(actions),
                notes=fake.text(max_nb_chars=200)
            )
            
            # Create occurrence event
            self._create_event(
                CLINICAL_AGGREGATE,
                patient.id,
                OCCURRENCE_RECORDED,
                {
                    'occurrence_id': str(occurrence.id),
                    'date': occurrence.date.isoformat(),
                    'type': occurrence.occurrence_type,
                    'description': occurrence.description,
                    'action_taken': occurrence.action_taken,
                    'notes': occurrence.notes
                }
            )

    def fake_date_within_year(self):
        """Generate a random date within the past year."""
        end_date = timezone.now().date()
        start_date = end_date - datetime.timedelta(days=365)
        days_between = (end_date - start_date).days
        random_days = random.randint(0, days_between)
        return start_date + datetime.timedelta(days=random_days)