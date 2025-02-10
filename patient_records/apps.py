from django.apps import AppConfig


class PatientRecordsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'patient_records'

    def ready(self):
        """Initialize app-specific configurations"""
        # Import and cache static lookups
        from .utils.cache_utils import cache_common_lookups
        cache_common_lookups()

        # Import signals
        from . import signals
