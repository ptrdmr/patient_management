from django.contrib import admin
from .models import (
    Patient, Provider, Vitals, CmpLabs, CbcLabs,
    ClinicalNote, PatientNote, NoteTag, NoteAttachment,
    Measurements, Symptoms, Imaging, Adls, Occurrences,
    Diagnosis, Visits, Medications, RecordRequestLog
)

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_number', 'first_name', 'last_name', 'date_of_birth', 'gender']
    list_filter = ['gender', 'created_at']
    search_fields = ['patient_number', 'first_name', 'last_name', 'email']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        ('Basic Information', {
            'fields': ['patient_number', 'first_name', 'middle_name', 'last_name', 'date_of_birth', 'gender']
        }),
        ('Contact Information', {
            'fields': ['address', 'phone', 'email']
        }),
        ('Additional Information', {
            'fields': ['emergency_contact', 'insurance_info']
        }),
        ('System Fields', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]

# Register other models
admin.site.register(Provider)
admin.site.register(Vitals)
admin.site.register(CmpLabs)
admin.site.register(CbcLabs)
admin.site.register(ClinicalNote)
admin.site.register(PatientNote)
admin.site.register(NoteTag)
admin.site.register(NoteAttachment)
admin.site.register(Measurements)
admin.site.register(Symptoms)
admin.site.register(Imaging)
admin.site.register(Adls)
admin.site.register(Occurrences)
admin.site.register(Diagnosis)
admin.site.register(Visits)
admin.site.register(Medications)
admin.site.register(RecordRequestLog)
