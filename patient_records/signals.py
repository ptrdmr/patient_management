from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Patient, AuditTrail

@receiver(post_save, sender=Patient)
def log_patient_save(sender, instance, created, **kwargs):
    action = 'CREATE' if created else 'UPDATE'
    changes = {field: getattr(instance, field) for field in instance._meta.fields}
    AuditTrail.objects.create(patient=instance, action=action, user=instance.modified_by, changes=changes)

@receiver(post_delete, sender=Patient)
def log_patient_delete(sender, instance, **kwargs):
    AuditTrail.objects.create(patient=instance, action='DELETE', user=instance.modified_by, changes={}) 