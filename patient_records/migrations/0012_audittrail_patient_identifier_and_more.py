# Generated by Django 5.1.3 on 2024-11-17 22:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient_records', '0011_alter_medications_dc_date_alter_medications_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='audittrail',
            name='patient_identifier',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='audittrail',
            name='patient',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='patient_records.patient'),
        ),
    ]
