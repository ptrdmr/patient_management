from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from patient_records.models import (
    Patient, Medications, CbcLabs, CmpLabs, 
    Symptoms, Diagnosis, Visits, Provider,
    Measurements, Imaging, Adls, Occurrences,
    ClinicalNotes, Vitals
)
from datetime import datetime, timedelta
from decimal import Decimal
import random
import uuid
from faker import Faker

class Command(BaseCommand):
    help = 'Generates test data for the patient management system'

    def __init__(self):
        super().__init__()
        self.fake = Faker()
        self.record_count = 100
        self.providers = []
        
    def handle(self, *args, **kwargs):
        self.stdout.write('Creating test data...')
        
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
        
        # Create test patients and their related records
        self.stdout.write('Creating patients and their records...')
        patients = self._create_patients()
        
        total = len(patients)
        for i, patient in enumerate(patients, 1):
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
            self._create_vitals(patient)
            
            if i % 10 == 0:
                self.stdout.write(f'Processed {i}/{total} patients')
            
        self.stdout.write(self.style.SUCCESS('Successfully created test data'))

    def _create_providers(self):
        for _ in range(10):
            provider = Provider.objects.create(
                date=self.fake.date_this_year(),
                provider=f"Dr. {self.fake.last_name()}"[:100],
                practice=self.fake.company()[:200],
                address=self.fake.street_address()[:255],
                city=self.fake.city()[:100],
                state=self.fake.state()[:100],
                zip=self.fake.zipcode()[:20],
                phone=self.fake.numerify(text='##########')[:20],
                fax=self.fake.numerify(text='##########')[:20],
                source='EMR'[:100]
            )
            self.providers.append(provider)

    def _create_patients(self):
        patients = []
        for _ in range(self.record_count):
            patient = Patient.objects.create(
                date=self.fake.date_this_year(),
                first_name=self.fake.first_name()[:50],
                last_name=self.fake.last_name()[:50],
                middle_name=self.fake.first_name()[:50],
                date_of_birth=self.fake.date_of_birth(),
                gender=random.choice(['M', 'F', 'O']),
                poa_name=f"{self.fake.first_name()} {self.fake.last_name()}"[:100],
                poa_contact=self.fake.phone_number()[:100],
                relationship=random.choice(['Spouse', 'Child', 'Sibling', 'Parent'])[:50],
                veteran=random.choice([True, False]),
                veteran_spouse=random.choice([True, False]),
                marital_status=random.choice(['Single', 'Married', 'Divorced', 'Widowed'])[:50],
                street_address=self.fake.street_address()[:255],
                city=self.fake.city()[:100],
                state=self.fake.state()[:100],
                zip=self.fake.zipcode()[:20],
                patient_phone=self.fake.phone_number()[:20],
                patient_email=self.fake.email(),
                allergies=random.choice(['None known', 'Penicillin', 'Peanuts', 'Latex']),
                code_status=random.choice(['Full Code', 'DNR', 'DNI'])[:50],
                ssn=self.fake.ssn()[:11],
                height_cm=Decimal(str(random.uniform(150, 200))).quantize(Decimal('.01')),
                height_inches=Decimal(str(random.uniform(59, 79))).quantize(Decimal('.01'))
            )
            patients.append(patient)
        return patients

    def _create_medications(self, patient):
        medications = [
            ('Lisinopril', ['5mg', '10mg', '20mg', '40mg']),
            ('Metformin', ['500mg', '850mg', '1000mg']),
            ('Amlodipine', ['2.5mg', '5mg', '10mg']),
            ('Omeprazole', ['20mg', '40mg']),
            ('Levothyroxine', ['25mcg', '50mcg', '75mcg', '100mcg'])
        ]
        for _ in range(random.randint(9, 24)):
            drug, doses = random.choice(medications)
            Medications.objects.create(
                id=str(uuid.uuid4()),
                patient=patient,
                date_prescribed=self.fake.date_this_year(),
                drug=drug,
                dose=random.choice(doses),
                route=random.choice(['PO', 'IV', 'IM', 'SC']),
                frequency=random.choice(['Daily', 'BID', 'TID', 'QID', 'PRN']),
                prn=random.choice([True, False]),
                dc_date=random.choice([None, self.fake.date_this_year()]),
                notes=self.fake.text(max_nb_chars=100)
            )

    def _create_cbc_labs(self, patient):
        for _ in range(random.randint(9, 24)):
            CbcLabs.objects.create(
                patient=patient,
                date=self.fake_date_within_year(),
                rbc=Decimal(str(random.uniform(4.0, 6.0))).quantize(Decimal('.01')),
                wbc=Decimal(str(random.uniform(4.0, 11.0))).quantize(Decimal('.01')),
                hemoglobin=Decimal(str(random.uniform(12.0, 17.0))).quantize(Decimal('.01')),
                hematocrit=Decimal(str(random.uniform(35.0, 50.0))).quantize(Decimal('.01')),
                mcv=Decimal(str(random.uniform(80.0, 100.0))).quantize(Decimal('.01')),
                mchc=Decimal(str(random.uniform(31.0, 37.0))).quantize(Decimal('.01')),
                rdw=Decimal(str(random.uniform(11.5, 14.5))).quantize(Decimal('.01')),
                platelets=Decimal(str(random.uniform(150, 450))).quantize(Decimal('.01')),
                mch=Decimal(str(random.uniform(27.0, 32.0))).quantize(Decimal('.01')),
                neutrophils=Decimal(str(random.uniform(40.0, 70.0))).quantize(Decimal('.01')),
                lymphocytes=Decimal(str(random.uniform(20.0, 40.0))).quantize(Decimal('.01')),
                monocytes=Decimal(str(random.uniform(2.0, 8.0))).quantize(Decimal('.01')),
                eosinophils=Decimal(str(random.uniform(1.0, 4.0))).quantize(Decimal('.01')),
                basophils=Decimal(str(random.uniform(0.5, 1.0))).quantize(Decimal('.01'))
            )

    def _create_cmp_labs(self, patient):
        for _ in range(random.randint(9, 24)):
            CmpLabs.objects.create(
                patient=patient,
                date=self.fake_date_within_year(),
                sodium=Decimal(str(random.uniform(135.0, 145.0))).quantize(Decimal('.01')),
                potassium=Decimal(str(random.uniform(3.5, 5.0))).quantize(Decimal('.01')),
                chloride=Decimal(str(random.uniform(96.0, 106.0))).quantize(Decimal('.01')),
                co2=Decimal(str(random.uniform(23.0, 29.0))).quantize(Decimal('.01')),
                glucose=Decimal(str(random.uniform(70.0, 100.0))).quantize(Decimal('.01')),
                bun=Decimal(str(random.uniform(7.0, 20.0))).quantize(Decimal('.01')),
                creatinine=Decimal(str(random.uniform(0.6, 1.2))).quantize(Decimal('.01')),
                calcium=Decimal(str(random.uniform(8.5, 10.5))).quantize(Decimal('.01')),
                protein=Decimal(str(random.uniform(6.0, 8.0))).quantize(Decimal('.01')),
                albumin=Decimal(str(random.uniform(3.5, 5.0))).quantize(Decimal('.01')),
                bilirubin=Decimal(str(random.uniform(0.3, 1.2))).quantize(Decimal('.01')),
                gfr=Decimal(str(random.uniform(90.0, 120.0))).quantize(Decimal('.01'))
            )

    def _create_symptoms(self, patient):
        symptoms_list = ['Fatigue', 'Headache', 'Nausea', 'Dizziness', 'Pain', 'Cough', 'Fever']
        for _ in range(random.randint(6, 18)):
            Symptoms.objects.create(
                id=str(uuid.uuid4()),
                patient=patient,
                date=self.fake.date_this_year(),
                symptom=random.choice(symptoms_list)[:200],
                notes=self.fake.text(max_nb_chars=100),
                source='Patient Report'[:100],
                person_reporting=random.choice(['Self', 'Family Member', 'Caregiver'])[:200]
            )

    def _create_diagnosis(self, patient):
        diagnoses = [
            ('Hypertension', 'I10'),
            ('Type 2 Diabetes', 'E11.9'),
            ('COPD', 'J44.9'),
            ('Osteoarthritis', 'M19.90'),
            ('Depression', 'F32.9')
        ]
        for _ in range(random.randint(3, 9)):
            diagnosis, icd = random.choice(diagnoses)
            Diagnosis.objects.create(
                patient=patient,
                date=self.fake.date_this_year(),
                diagnosis=diagnosis[:255],
                icd_code=icd[:10],
                notes=self.fake.text(max_nb_chars=100)
            )

    def _create_visits(self, patient):
        visit_types = ['Follow-up', 'New Patient', 'Urgent', 'Routine']
        for _ in range(random.randint(6, 15)):
            Visits.objects.create(
                id=str(uuid.uuid4()),
                patient=patient,
                provider=random.choice(self.providers),
                date=self.fake.date_this_year(),
                visit_type=random.choice(visit_types)[:100],
                practice=self.fake.company()[:200],
                notes=self.fake.text(max_nb_chars=100),
                source='EMR'[:100]
            )

    def _create_measurements(self, patient):
        for _ in range(random.randint(6, 12)):
            Measurements.objects.create(
                id=str(uuid.uuid4()),
                patient=patient,
                date=self.fake.date_this_year(),
                weight=Decimal(str(random.uniform(50.0, 120.0))).quantize(Decimal('.1')),
                source='Nursing'[:100],
                nutritional_intake=random.choice(['Good', 'Fair', 'Poor'])[:200],
                mac=str(random.uniform(20.0, 35.0))[:100],
                fast=random.choice(['0', '1', '2', '3'])[:100],
                pps=random.choice(['100', '90', '80', '70'])[:100],
                plof=random.choice(['Independent', 'Assisted', 'Dependent'])[:100]
            )

    def _create_imaging(self, patient):
        imaging_types = ['X-Ray', 'CT', 'MRI', 'Ultrasound']
        for _ in range(random.randint(3, 9)):
            Imaging.objects.create(
                id=str(uuid.uuid4()),
                patient=patient,
                date=self.fake.date_this_year(),
                type=random.choice(imaging_types)[:100],
                notes=self.fake.text(max_nb_chars=100),
                source='Radiology'[:100]
            )

    def _create_adls(self, patient):
        status_choices = ['Independent', 'Needs Assistance', 'Dependent']
        for _ in range(random.randint(6, 12)):
            Adls.objects.create(
                id=str(uuid.uuid4()),
                patient=patient,
                date=self.fake.date_this_year(),
                ambulation=random.choice(status_choices)[:100],
                continence=random.choice(status_choices)[:100],
                transfer=random.choice(status_choices)[:100],
                dressing=random.choice(status_choices)[:100],
                feeding=random.choice(status_choices)[:100],
                bathing=random.choice(status_choices)[:100],
                notes=self.fake.text(max_nb_chars=100),
                source='Nursing Assessment'[:100]
            )

    def _create_occurrences(self, patient):
        occurrence_types = ['Fall', 'Medication Error', 'Skin Breakdown', 'Behavioral Issue']
        for _ in range(random.randint(3, 6)):
            Occurrences.objects.create(
                id=str(uuid.uuid4()),
                patient=patient,
                date=self.fake.date_this_year(),
                occurrence_type=random.choice(occurrence_types)[:100],
                description=self.fake.text(max_nb_chars=100),
                notes=self.fake.text(max_nb_chars=100),
                source='Staff Report'[:100]
            )

    def _create_clinical_notes(self, patient):
        for _ in range(random.randint(6, 15)):
            ClinicalNotes.objects.create(
                patient=patient,
                date=self.fake.date_this_year(),
                provider=random.choice(self.providers),
                notes=self.fake.paragraph(nb_sentences=5),
                source='manual'[:100]
            )

    def _create_vitals(self, patient):
        for _ in range(random.randint(9, 24)):
            Vitals.objects.create(
                id=str(uuid.uuid4()),
                patient=patient,
                date=self.fake_date_within_year(),
                blood_pressure=f"{random.randint(90, 140)}/{random.randint(60, 90)}",
                temperature=round(random.uniform(97.0, 99.9), 1),
                spo2=random.randint(95, 100),
                pulse=random.randint(60, 100),
                respirations=random.randint(12, 20),
                supp_o2=random.choice([True, False]),
                pain=random.randint(0, 10),
                source='Nursing'[:100]
            )

    def fake_date_within_year(self):
        """Generate a date within the last year"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        return self.fake.date_between(start_date=start_date, end_date=end_date)