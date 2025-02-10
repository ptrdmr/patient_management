# Codebase Remediation Plan

## Table of Contents
1. [Form Submission Fixes](#1-form-submission-fixes)
2. [Data Display Restoration](#2-data-display-restoration)
3. [Navigation Integrity](#3-navigation-integrity)
4. [Component Separation](#4-component-separation) 
5. [Event Sourcing Compliance](#5-event-sourcing-compliance)
6. [Testing Strategy](#6-testing-strategy)
7. [Post-Implementation Steps](#7-post-implementation-steps)

## 1. Form Submission Fixes 🛠️
### Target Files:
- `templates/patient_records/add_vitals.html` (Lines 1-2)
- `templates/patient_records/add_diagnosis.html` (Lines 1-86)
- `views/clinical_entries.py`

### Implementation Steps:
1. Update form methods to POST:
html
<!-- In form templates -->
<form method="post" action="{% url 'save_vitals' %}">
{% csrf_token %}
<!-- Existing form fields -->
</form>

2. Add form validation logging:
python
def form_valid(self, form):
logger.debug(f"Form submission received: {form.cleaned_data}")
messages.success(self.request, 'Entry saved successfully')
return super().form_valid(form)

3. Implement message display:
html
<div class="alert alert-{{ message.tags }} alert-dismissible">
{{ message }}
<button type="button" class="close" data-dismiss="alert">&times;</button>
</div>


### Verification Checklist:
- [ ] All forms submit via POST
- [ ] CSRF tokens present
- [ ] Success messages appear
- [ ] Form data persists in database

## 2. Data Display Restoration 🔍
### Critical Files:
- `models/clinical.py`
- `templates/patient_records/partials/_clinical.html`

### Implementation Steps:
1. Update model fields:
python
class Symptom(models.Model):
source = models.CharField(max_length=100, null=True, default='patient')
person_reporting = models.CharField(max_length=100, null=True)
# ... existing fields ...


2. Add template fallbacks:
html
<td>{% if symptom.source %}{{ symptom.source }}{% else %}Patient Reported{% endif %}</td>
<td>{{ symptom.person_reporting|default:"Not Specified" }}</td>

3. Update view context:
python
def get_context_data(self, kwargs):
context = super().get_context_data(kwargs)
context['symptoms'] = Symptom.objects.select_related('patient').filter(
patient=self.object
)
return context


### Verification Checklist:
- [ ] All fields display values or defaults
- [ ] Null handling works correctly
- [ ] Related data loads efficiently

## 3. Navigation Integrity 🧭
### Target Components:
- `static/js/patient_detail.js`
- `urls.py`

### Implementation Steps:
1. Add tab persistence:
javascript
// Tab state management
function persistActiveTab() {
const activeTab = localStorage.getItem('activePatientTab');
if(activeTab) {
$(a[href="${activeTab}"]).tab('show');
}
}
$(document).ready(() => {
persistActiveTab();
$('.nav-tabs a').on('shown.bs.tab', (e) => {
localStorage.setItem('activePatientTab', $(e.target).attr('href'));
});
});

2. Update view success URLs:
python
def get_success_url(self):
next_url = self.request.GET.get('next')
if next_url and is_safe_url(next_url, allowed_hosts=None):
return next_url
return reverse('patient-detail', kwargs={'pk': self.object.patient.id})
python
urlpatterns = [
path('labs/cmp/', CMPLabView.as_view(), name='cmp-form'),
path('labs/cbc/', CBCLabView.as_view(), name='cbc-form'),
]
python
class CMPHandler(LabHandlerBase):
template_name = 'labs/cmp_form.html'
lab_type = 'cmp'
class CBCHandler(LabHandlerBase):
template_name = 'labs/cbc_form.html'
lab_type = 'cbc'
python
def project_patient_data(event):
if event.type == 'PatientUpdated':
PatientReadModel.objects.update_or_create(
id=event.aggregate_id,
defaults={'current_data': event.data}
)
python
class ReplayEvents(BaseCommand):
def handle(self, args, options):
for event in EventStore.objects.order_by('timestamp'):
project_patient_data(event)
python
class FormSubmissionTests(TestCase):
def test_vitals_form_submission(self):
data = {'blood_pressure': '120/80', 'temperature': 98.6}
response = self.client.post(reverse('save-vitals'), data)
self.assertEqual(response.status_code, 302)
self.assertTrue(Vitals.objects.filter(blood_pressure='120/80').exists())
python
class NavigationTests(TestCase):
def test_tab_persistence(self):
response = self.client.get(reverse('patient-detail'))
self.assertContains(response, 'persistActiveTab')
bash
python manage.py makemigrations
python manage.py migrate
bash
python manage.py clear_cache
bash
python manage.py collectstatic --noinput


### Verification Checklist:
- [ ] Tabs persist across page reloads
- [ ] Cancel returns to correct tab
- [ ] URLs resolve correctly

## 4. Component Separation 🧩
### Implementation Targets:
- `urls.py`
- `handlers/lab_processing.py`
- `templates/labs/`

### Implementation Steps:
1. Split URL patterns:
python
urlpatterns = [
path('labs/cmp/', CMPLabView.as_view(), name='cmp-form'),
path('labs/cbc/', CBCLabView.as_view(), name='cbc-form'),
]
2. Create separate handlers:
python
class CMPHandler(LabHandlerBase):
template_name = 'labs/cmp_form.html'
lab_type = 'cmp'
class CBCHandler(LabHandlerBase):
template_name = 'labs/cbc_form.html'
lab_type = 'cbc'


### Verification Checklist:
- [ ] Separate routes work
- [ ] Forms process independently
- [ ] Navigation reflects separation

## 5. Event Sourcing Compliance 🏛️
### Critical Files:
- `models/events.py`
- `projections/`
- `handlers/event_handlers.py`

### Implementation Steps:
1. Create read model projections:
python
def project_patient_data(event):
if event.type == 'PatientUpdated':
PatientReadModel.objects.update_or_create(
id=event.aggregate_id,
defaults={'current_data': event.data}
)


2. Add event replay capability:
python
class ReplayEvents(BaseCommand):
def handle(self, args, options):
for event in EventStore.objects.order_by('timestamp'):
project_patient_data(event)


### Verification Checklist:
- [ ] Events store correctly
- [ ] Projections update
- [ ] Replay works correctly

## 6. Testing Strategy 🧪
### Test Files:
- `tests/test_forms.py`
- `tests/test_navigation.py`
- `tests/test_event_sourcing.py`

### Implementation Steps:
1. Form submission tests:
python
class FormSubmissionTests(TestCase):
def test_vitals_form_submission(self):
data = {'blood_pressure': '120/80', 'temperature': 98.6}
response = self.client.post(reverse('save-vitals'), data)
self.assertEqual(response.status_code, 302)
self.assertTrue(Vitals.objects.filter(blood_pressure='120/80').exists())

2. Navigation tests:
python
class NavigationTests(TestCase):
def test_tab_persistence(self):
response = self.client.get(reverse('patient-detail'))
self.assertContains(response, 'persistActiveTab')


### Verification Checklist:
- [ ] All tests pass
- [ ] Coverage > 85%
- [ ] CI pipeline succeeds

## 7. Post-Implementation Steps
1. Run Migrations:

bash
python manage.py makemigrations
python manage.py migrate

2. Clear Caches:
bash
python manage.py clear_cache


3. Collect Static Files:

4. Verify Audit Trail:
- [ ] Check event store integrity
- [ ] Verify read model consistency
- [ ] Validate audit logs

5. Medical Data Validation:
- [ ] Verify data retention policies
- [ ] Check HIPAA compliance
- [ ] Validate data encryption

### Final Checklist:
- [ ] All forms working
- [ ] Navigation smooth
- [ ] Data displaying correctly
- [ ] Tests passing
- [ ] Event sourcing compliant
- [ ] Performance metrics met