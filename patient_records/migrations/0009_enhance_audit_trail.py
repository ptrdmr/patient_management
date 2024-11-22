from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('patient_records', '0008_clinicalnotes'),  # Based on your last migration
    ]

    operations = [
        # Step 1: Add new fields without modifying existing data
        migrations.AddField(
            model_name='audittrail',
            name='record_type',
            field=models.CharField(
                choices=[
                    ('PATIENT', 'Patient Demographics'),
                    ('CLINICAL_NOTE', 'Clinical Notes'),
                    ('CBC_LAB', 'CBC Lab Results'),
                    ('CMP_LAB', 'CMP Lab Results'),
                    ('MEDICATION', 'Medications'),
                    ('SYMPTOM', 'Symptoms'),
                ],
                max_length=20,
                default='PATIENT'  # Safe default for existing records
            ),
        ),
        migrations.AddField(
            model_name='audittrail',
            name='ip_address',
            field=models.GenericIPAddressField(null=True),
        ),
        migrations.AddField(
            model_name='audittrail',
            name='previous_values',
            field=models.JSONField(default=dict),
        ),
        
        # Step 2: Modify action field to include VIEW
        migrations.AlterField(
            model_name='audittrail',
            name='action',
            field=models.CharField(
                max_length=10,
                choices=[
                    ('CREATE', 'Create'),
                    ('UPDATE', 'Update'),
                    ('DELETE', 'Delete'),
                    ('VIEW', 'View'),
                ],
            ),
        ),
        
        # Step 3: Rename existing changes field to new_values
        migrations.RenameField(
            model_name='audittrail',
            old_name='changes',
            new_name='new_values',
        ),
        
        # Step 4: Add performance indexes
        migrations.AddIndex(
            model_name='audittrail',
            index=models.Index(fields=['patient', '-timestamp'], name='audit_patient_ts_idx'),
        ),
        migrations.AddIndex(
            model_name='audittrail',
            index=models.Index(fields=['user', '-timestamp'], name='audit_user_ts_idx'),
        ),
        migrations.AddIndex(
            model_name='audittrail',
            index=models.Index(fields=['record_type', '-timestamp'], name='audit_type_ts_idx'),
        ),
    ]