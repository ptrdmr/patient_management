# Forms and Validation

## Overview
This document details the form handling and validation logic used throughout the Patient Management System. Forms are crucial for data entry and validation across all modules.

## Core Forms

### Patient Forms

#### Patient Registration
```python
class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'date_of_birth',
            'gender', 'address', 'phone', 'email',
            'allergies', 'code_status'
        ]
        
    def clean_date_of_birth(self):
        """Validate date is not in future"""
        dob = self.cleaned_data['date_of_birth']
        if dob > date.today():
            raise ValidationError("Date of birth cannot be in the future")
        return dob
```
→ [[Patient Forms|Patient Form Documentation]]

### Clinical Forms

#### Vital Signs Form
```python
class VitalsForm(forms.ModelForm):
    class Meta:
        model = Vitals
        fields = [
            'blood_pressure', 'temperature', 'spo2',
            'pulse', 'respirations'
        ]
        
    def clean_spo2(self):
        """Validate SpO2 is within normal range"""
        spo2 = self.cleaned_data['spo2']
        if not (0 <= spo2 <= 100):
            raise ValidationError("SpO2 must be between 0 and 100")
        return spo2
```
→ [[Vitals Form|Vital Signs Form Documentation]]

#### Laboratory Forms
```python
class CmpLabForm(forms.ModelForm):
    class Meta:
        model = CmpLabs
        fields = [
            'sodium', 'potassium', 'chloride',
            'co2', 'bun', 'creatinine'
        ]
        
class CbcLabForm(forms.ModelForm):
    class Meta:
        model = CbcLabs
        fields = [
            'wbc', 'rbc', 'hemoglobin',
            'hematocrit', 'platelets'
        ]
```
→ [[Lab Forms|Laboratory Forms Documentation]]

## Validation Patterns

### Client-Side Validation
```javascript
// Example of client-side validation
function validateVitals() {
    const spo2 = document.getElementById('id_spo2').value;
    if (spo2 < 0 || spo2 > 100) {
        showError('SpO2 must be between 0 and 100');
        return false;
    }
    return true;
}
```

### Server-Side Validation
```python
def clean(self):
    cleaned_data = super().clean()
    systolic = cleaned_data.get('systolic')
    diastolic = cleaned_data.get('diastolic')
    
    if systolic and diastolic:
        if diastolic > systolic:
            raise ValidationError(
                "Diastolic pressure cannot be higher than systolic"
            )
```

## Form Widgets

### Custom Date Widget
```python
class DatePickerWidget(forms.DateInput):
    """Custom date picker with validation"""
    template_name = 'widgets/datepicker.html'
    input_type = 'date'
```

### Time Input Widget
```python
class TimePickerWidget(forms.TimeInput):
    """Custom time picker for procedure times"""
    template_name = 'widgets/timepicker.html'
    input_type = 'time'
```

## Form Processing

### Form Handling Pattern
```python
@require_http_methods(['GET', 'POST'])
def handle_form(request):
    if request.method == 'POST':
        form = MyForm(request.POST)
        if form.is_valid():
            instance = form.save()
            messages.success(request, "Data saved successfully")
            return redirect('success_url')
    else:
        form = MyForm()
    return render(request, 'template.html', {'form': form})
```

## Error Handling

### Form Errors
```python
def form_error_handler(form):
    """Process and format form errors"""
    errors = {}
    for field, error_list in form.errors.items():
        errors[field] = [str(error) for error in error_list]
    return errors
```

### AJAX Form Handling
```python
def ajax_form_handler(request):
    """Handle AJAX form submissions"""
    form = MyForm(request.POST)
    if form.is_valid():
        instance = form.save()
        return JsonResponse({'success': True})
    return JsonResponse({
        'success': False,
        'errors': form_error_handler(form)
    })
```

## Form Mixins

### Audit Mixin
```python
class AuditFormMixin:
    """Add audit trail to form processing"""
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            create_audit_trail(instance, 'create', self.user)
        return instance
```

## Form Templates

### Base Form Template
```html
{% extends "base.html" %}
{% block content %}
<form method="post" novalidate>
    {% csrf_token %}
    {{ form.non_field_errors }}
    {% for field in form %}
    <div class="form-group">
        {{ field.label_tag }}
        {{ field }}
        {{ field.errors }}
    </div>
    {% endfor %}
    <button type="submit">Submit</button>
</form>
{% endblock %}
```

## Related Documentation
- [[Form Validation|Validation Rules]]
- [[Widget Guide|Custom Widgets]]
- [[Error Handling|Error Processing]]
- [[AJAX Forms|AJAX Implementation]]

## Tags
#forms #validation #django #documentation 