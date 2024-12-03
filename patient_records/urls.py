# urls.py
from django.urls import path
from . import views

urlpatterns = [
    
    # Home page
    path('home/', views.home, name='home'),
    
    # Patient related URLs
    path('patient/add/', views.add_patient, name='add_patient'),
    path('patients/', views.patient_list, name='patient_list'),
    path('patient/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    
    # Clinical data entry URLs
    path('patient/<int:patient_id>/diagnosis/add/', views.add_diagnosis, name='add_diagnosis'),
    path('patient/<int:patient_id>/vitals/add/', views.vital_signs_form, name='add_vitals'),
    path('patient/<int:patient_id>/cmp-labs/add/', views.add_cmp_labs, name='add_cmp_labs'),
    path('patient/<int:patient_id>/cbc-labs/add/', views.add_cbc_labs, name='add_cbc_labs'),
    path('patient/<int:patient_id>/medications/add/', views.add_medications, name='add_medications'),
    path('patient/<int:patient_id>/measurements/add/', views.add_measurements, name='add_measurements'),
    path('patient/<int:patient_id>/adls/add/', views.add_adls, name='add_adls'),
    path('patient/<int:patient_id>/symptoms/add/', views.add_symptoms, name='add_symptoms'),
    path('patient/<int:patient_id>/occurrence/add/', views.add_occurrence, name='add_occurrence'),
    path('patient/<int:patient_id>/imaging/add/', views.add_imaging, name='add_imaging'),
    path('patient/<int:patient_id>/visit/add/', views.add_visit, name='add_visit'),
    path('patient/<int:patient_id>/adls/add/', views.add_adls, name='add_adls'),
    path('patient/<int:patient_id>/imaging/add/', views.add_imaging, name='add_imaging'),
    path('patient/<int:patient_id>/record-request/add/', views.add_record_request, name='add_record_request'),
    
    # Provider related URLs
    path('provider/add/', views.add_provider, name='add_provider'),
    path('providers/', views.provider_list, name='provider_list'),
    path('provider/<int:pk>/edit/', views.edit_provider, name='edit_provider'),
    
    # API endpoints
    path('api/icd-lookup/', views.icd_code_lookup, name='icd_code_lookup'),
    
    # Tab data
    path('patient/<int:patient_id>/tab/<str:tab_name>/', views.patient_tab_data, name='patient_tab_data'),
    
    # Notes URLs
    path('patient/notes/', views.patient_notes, name='patient_notes'),
    path('patient/notes/<int:note_id>/', views.get_note_detail, name='get_note_detail'),
    path('patient/notes/create/', views.create_note, name='create_note'),
    path('patient/notes/<int:note_id>/edit/', views.edit_note, name='edit_note'),
    path('patient/notes/<int:note_id>/delete/', views.delete_note, name='delete_note'),
    path('patient/notes/<int:note_id>/toggle-pin/', views.toggle_pin_note, name='toggle_pin_note'),
]