from django.core.management.base import BaseCommand
from patient_records.models import Patient, Medications
from datetime import datetime, timedelta
import random
import uuid

class Command(BaseCommand):
    help = 'Generates test medication records for a patient'

    def add_arguments(self, parser):
        parser.add_argument('patient_id', type=int)
        parser.add_argument('record_count', type=int)

    def handle(self, *args, **options):
        patient_id = options['patient_id']
        record_count = options['record_count']
        
        patient = Patient.objects.get(id=patient_id)
        
        medications = []
        date = datetime.now()
        
        drugs = ['Aspirin', 'Ibuprofen', 'Acetaminophen', 'Amoxicillin']
        doses = ['100mg', '200mg', '500mg', '1000mg']
        routes = ['Oral', 'IV', 'IM', 'Topical']
        frequencies = ['Daily', 'BID', 'TID', 'QID', 'PRN']
        
        for i in range(record_count):
            medications.append(Medications(
                id=str(uuid.uuid4()),  # Generate unique ID
                patient=patient,
                date_prescribed=date - timedelta(days=i),
                drug=random.choice(drugs),
                dose=random.choice(doses),
                route=random.choice(routes),
                frequency=random.choice(frequencies),
                prn=random.choice([True, False]),
                notes=f'Test medication record {i}'
            ))
            
        # Use smaller batch size to avoid memory issues
        batch_size = 1000
        for i in range(0, len(medications), batch_size):
            batch = medications[i:i + batch_size]
            Medications.objects.bulk_create(batch)
            self.stdout.write(f'Created records {i+1} to {min(i+batch_size, record_count)}')
            
        self.stdout.write(self.style.SUCCESS(f'Successfully created {record_count} medication records')) 