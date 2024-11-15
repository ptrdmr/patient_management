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
    path('patient/<str:patient_id>/diagnosis/add/', views.add_diagnosis, name='add_diagnosis'),
    path('patient/<str:patient_id>/vitals/add/', views.add_vitals, name='add_vitals'),
    path('patient/<str:patient_id>/labs/add/', views.add_labs, name='add_labs'),
    path('patient/<str:patient_id>/medications/add/', views.add_medications, name='add_medications'),
    path('patient/<str:patient_id>/measurements/add/', views.add_measurements, name='add_measurements'),
    path('patient/<str:patient_id>/adls/add/', views.add_adls, name='add_adls'),
    path('patient/<str:patient_id>/symptoms/add/', views.add_symptoms, name='add_symptoms'),
    path('patient/<str:patient_id>/occurrence/add/', views.add_occurrence, name='add_occurrence'),
    path('patient/<str:patient_id>/imaging/add/', views.add_imaging, name='add_imaging'),
    
    # Provider related URLs
    path('provider/add/', views.add_provider, name='add_provider'),
    path('providers/', views.provider_list, name='provider_list'),
    path('provider/<int:provider_id>/edit/', views.edit_provider, name='edit_provider'),
    path('api/icd-lookup/', views.icd_code_lookup, name='icd_code_lookup'),
    path('delete-record/<str:model_name>/<int:record_id>/', views.delete_record, name='delete_record'),
    path('patient/<int:patient_id>/tab/<str:tab_name>/', views.patient_tab_data, name='patient_tab_data'),
]