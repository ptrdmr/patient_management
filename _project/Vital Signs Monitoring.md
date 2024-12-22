# Vital Signs Monitoring

## Overview
The Vital Signs Monitoring module manages patient vital signs tracking, trending, and alerting functionality.

## Core Features

### Vital Signs Recording
```python
class VitalSigns(models.Model):
    """Model for tracking patient vital signs."""
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    recorded_by = models.ForeignKey('Staff', on_delete=models.PROTECT)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    # Core vitals
    temperature = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        help_text="Temperature in Fahrenheit"
    )
    pulse = models.IntegerField(
        help_text="Heart rate in beats per minute"
    )
    respiration = models.IntegerField(
        help_text="Respirations per minute"
    )
    blood_pressure_systolic = models.IntegerField()
    blood_pressure_diastolic = models.IntegerField()
    oxygen_saturation = models.IntegerField(
        help_text="SpO2 percentage"
    )
    
    # Additional measurements
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight in pounds"
    )
    height = models.IntegerField(
        null=True,
        blank=True,
        help_text="Height in inches"
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['patient', 'recorded_at']),
        ]
```

## Vital Signs Analysis

### Trend Analysis
```python
def analyze_vital_trends(patient_id, days=30):
    """Analyze vital signs trends over time."""
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    vitals = VitalSigns.objects.filter(
        patient_id=patient_id,
        recorded_at__range=(start_date, end_date)
    ).order_by('recorded_at')
    
    return {
        'temperature_trend': calculate_trend(vitals, 'temperature'),
        'pulse_trend': calculate_trend(vitals, 'pulse'),
        'bp_trend': calculate_bp_trend(vitals),
        'oxygen_trend': calculate_trend(vitals, 'oxygen_saturation')
    }

def calculate_trend(vitals_queryset, field_name):
    """Calculate trend for a specific vital sign."""
    values = list(vitals_queryset.values_list(field_name, flat=True))
    dates = list(vitals_queryset.values_list('recorded_at', flat=True))
    
    return {
        'values': values,
        'dates': dates,
        'average': sum(values) / len(values) if values else 0,
        'min': min(values) if values else None,
        'max': max(values) if values else None
    }
```

## Alert System

### Vital Signs Alerts
```python
class VitalSignAlert(models.Model):
    """Model for vital signs alerts."""
    SEVERITY_CHOICES = [
        ('CRITICAL', 'Critical'),
        ('WARNING', 'Warning'),
        ('NOTICE', 'Notice')
    ]
    
    vital_sign = models.ForeignKey('VitalSigns', on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=50)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_by = models.ForeignKey(
        'Staff',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)

def check_vital_signs_alerts(vital_signs):
    """Check vital signs for alert conditions."""
    alerts = []
    
    # Temperature alerts
    if vital_signs.temperature >= 103:
        alerts.append(VitalSignAlert(
            vital_sign=vital_signs,
            alert_type='HIGH_TEMP',
            severity='CRITICAL',
            message=f'High temperature: {vital_signs.temperature}°F'
        ))
    
    # Blood pressure alerts
    if vital_signs.blood_pressure_systolic >= 180:
        alerts.append(VitalSignAlert(
            vital_sign=vital_signs,
            alert_type='HIGH_BP',
            severity='CRITICAL',
            message=f'High blood pressure: {vital_signs.blood_pressure_systolic}/{vital_signs.blood_pressure_diastolic}'
        ))
    
    # Oxygen saturation alerts
    if vital_signs.oxygen_saturation < 90:
        alerts.append(VitalSignAlert(
            vital_sign=vital_signs,
            alert_type='LOW_O2',
            severity='CRITICAL',
            message=f'Low oxygen saturation: {vital_signs.oxygen_saturation}%'
        ))
    
    return alerts
```

## Reporting

### Vital Signs Report
```python
def generate_vitals_report(patient_id, start_date, end_date):
    """Generate vital signs report for specified period."""
    vitals = VitalSigns.objects.filter(
        patient_id=patient_id,
        recorded_at__range=(start_date, end_date)
    ).order_by('recorded_at')
    
    alerts = VitalSignAlert.objects.filter(
        vital_sign__patient_id=patient_id,
        created_at__range=(start_date, end_date)
    ).order_by('-created_at')
    
    return {
        'vitals_data': vitals,
        'alerts': alerts,
        'summary': {
            'total_readings': vitals.count(),
            'critical_alerts': alerts.filter(severity='CRITICAL').count(),
            'warning_alerts': alerts.filter(severity='WARNING').count()
        }
    }
```

## Data Visualization

### Vital Signs Chart
```javascript
function renderVitalsChart(data) {
    const ctx = document.getElementById('vitals-chart').getContext('2d');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.dates,
            datasets: [
                {
                    label: 'Temperature',
                    data: data.temperature_values,
                    borderColor: 'rgb(255, 99, 132)'
                },
                {
                    label: 'Pulse',
                    data: data.pulse_values,
                    borderColor: 'rgb(54, 162, 235)'
                },
                {
                    label: 'O2 Saturation',
                    data: data.oxygen_values,
                    borderColor: 'rgb(75, 192, 192)'
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
}
```

## Related Documentation
- [[Patient Records & Demographics]]
- [[Clinical Information Management]]
- [[API Reference]]
- [[Monitoring Guide]]

## Tags
#vital-signs #patient-monitoring #alerts #trends 