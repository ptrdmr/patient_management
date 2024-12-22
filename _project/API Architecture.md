# API Architecture

## Overview
This document outlines the API architecture of the Patient Management System, focusing on patient data input and medical record management.

## Core API Endpoints

### Patient Demographics
```python
class PatientDemographicsViewSet(viewsets.ModelViewSet):
    """
    API endpoint for patient demographics management
    """
    queryset = PatientDemographics.objects.all()
    serializer_class = PatientDemographicsSerializer
    
    def get_queryset(self):
        return self.queryset.filter(
            Q(id=self.kwargs.get('pk')) |
            Q(patient_id=self.kwargs.get('patient_pk'))
        )
```

### Medical Records
```python
class MedicalRecordViewSet(viewsets.ModelViewSet):
    """
    API endpoint for medical records
    """
    serializer_class = MedicalRecordSerializer
    
    def get_queryset(self):
        return MedicalRecord.objects.filter(
            patient_id=self.kwargs.get('patient_pk')
        ).select_related('provider')
```

### Lab Results
```python
class LabResultViewSet(viewsets.ModelViewSet):
    """
    API endpoint for lab results (CMP and CBC)
    """
    def get_queryset(self):
        lab_type = self.kwargs.get('lab_type')
        if lab_type == 'cmp':
            return CMPLabs.objects.filter(patient_id=self.kwargs.get('patient_pk'))
        elif lab_type == 'cbc':
            return CBCLabs.objects.filter(patient_id=self.kwargs.get('patient_pk'))
```

## Data Validation

### Patient Data Validation
```python
class PatientDemographicsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientDemographics
        fields = [
            'id', 'date', 'allergies', 'code_status',
            'poa_name', 'relationship', 'poa_contact',
            'veteran', 'veteran_spouse', 'marital_status',
            'street_address', 'city', 'state', 'zip',
            'patient_phone', 'patient_email'
        ]
    
    def validate_patient_phone(self, value):
        if not re.match(r'^\(\d{3}\) \d{3}-\d{4}$', value):
            raise ValidationError("Phone must be in format (XXX) XXX-XXXX")
        return value
```

### Lab Results Validation
```python
class CMPLabsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CMPLabs
        fields = [
            'id', 'date', 'bun', 'globulin', 'ag_ratio',
            'alk_phos', 'ast', 'alt', 'sodium', 'calcium',
            'protein', 'albumin', 'bilirubin', 'gfr',
            'potassium', 'chloride', 'co2', 'glucose',
            'creatinine'
        ]
    
    def validate_glucose(self, value):
        if value < 0:
            raise ValidationError("Glucose cannot be negative")
        return value
```

## Authentication & Authorization

### JWT Configuration
```python
JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': timedelta(hours=8),
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=7),
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
}
```

### Permission Classes
```python
class PatientRecordAccess(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.provider == request.user.provider
```

## API Documentation

### Swagger Configuration
```python
schema_view = get_schema_view(
    openapi.Info(
        title="Patient Management API",
        default_version='v1',
        description="API for patient records and medical data management"
    ),
    public=True,
    permission_classes=[permissions.IsAuthenticated],
)
```

## Related Documentation
- [[Patient Records & Demographics]]
- [[Laboratory Data Management]]
- [[Clinical Information Management]]

## Tags
#api #medical-records #lab-results #patient-data