# Generated by Django 5.1.3 on 2024-11-12 03:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient_records', '0007_medications_patient_rec_date_pr_b647ed_idx_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClinicalNotes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('notes', models.TextField()),
                ('source', models.CharField(default='manual', max_length=100)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patient_records.patient')),
                ('provider', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='patient_records.provider')),
            ],
            options={
                'verbose_name': 'Clinical Note',
                'verbose_name_plural': 'Clinical Notes',
                'ordering': ['-date'],
                'indexes': [models.Index(fields=['-date'], name='patient_rec_date_17d5cb_idx'), models.Index(fields=['patient', '-date'], name='patient_rec_patient_519e96_idx')],
            },
        ),
    ]
