from django.db import migrations, models
import uuid

class Migration(migrations.Migration):
    dependencies = [
        ('patient_records', '0020_notetag_patientnote_noteattachment_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventStore',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True)),
                ('aggregate_id', models.UUIDField()),
                ('aggregate_type', models.CharField(max_length=100)),
                ('event_type', models.CharField(max_length=100)),
                ('event_data', models.JSONField()),
                ('metadata', models.JSONField(null=True)),
                ('version', models.IntegerField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'indexes': [
                    models.Index(fields=['aggregate_id', 'version'], name='event_store_agg_ver_idx'),
                    models.Index(fields=['timestamp'], name='event_store_timestamp_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='PatientReadModel',
            fields=[
                ('id', models.UUIDField(primary_key=True)),
                ('current_data', models.JSONField()),
                ('last_updated', models.DateTimeField()),
                ('version', models.IntegerField()),
                ('snapshot_data', models.JSONField(null=True)),
                ('snapshot_version', models.IntegerField(null=True)),
            ],
            options={
                'indexes': [
                    models.Index(fields=['last_updated'], name='patient_last_updated_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='ClinicalReadModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True)),
                ('patient_id', models.UUIDField()),
                ('event_type', models.CharField(max_length=100)),
                ('data', models.JSONField()),
                ('recorded_at', models.DateTimeField()),
                ('schema_version', models.CharField(default='1.0', max_length=10)),
            ],
            options={
                'indexes': [
                    models.Index(fields=['patient_id', 'recorded_at'], name='clinical_patient_time_idx'),
                    models.Index(fields=['event_type', 'recorded_at'], name='clinical_event_time_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='LabResultsReadModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True)),
                ('patient_id', models.UUIDField()),
                ('lab_type', models.CharField(max_length=50)),
                ('results', models.JSONField()),
                ('performed_at', models.DateTimeField()),
                ('schema_version', models.CharField(default='1.0', max_length=10)),
            ],
            options={
                'indexes': [
                    models.Index(fields=['patient_id', 'performed_at'], name='lab_patient_time_idx'),
                    models.Index(fields=['lab_type', 'performed_at'], name='lab_type_time_idx'),
                ],
            },
        ),
        migrations.AddConstraint(
            model_name='eventstore',
            constraint=models.UniqueConstraint(
                fields=['aggregate_id', 'version'],
                name='unique_aggregate_version'
            ),
        ),
    ] 