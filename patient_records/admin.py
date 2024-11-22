from django.contrib import admin
from .models import Patient, AuditTrail

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'poa_name', 'poa_contact', 'date')

@admin.register(AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):
    list_display = ('patient', 'action', 'user', 'timestamp')
    list_filter = ('action', 'user')
    search_fields = ('patient__poa_name', 'user__username')
