# Static Files Reference Guide

## Core Styles
- `css/core/variables.css`: Global CSS variables for consistent theming
  - Colors, spacing, borders, and text styles
  - Lines: 1-27

- `css/core/reset.css`: Basic CSS reset for consistent rendering
  - Removes default margins, sets box-sizing
  - Lines: 1-30

- `css/core/layout.css`: Base layout structure
  - Content padding, header styles
  - Lines: 1-25

## Shared Components
- `css/shared/forms.css`: Form styling and validation states
  - Form layouts, inputs, validation states
  - Lines: 1-150

- `css/shared/buttons.css`: Button styles and states
  - Primary, secondary, danger buttons
  - Lines: 1-55

- `css/shared/cards.css`: Card component styles
  - Data cards, headers, content areas
  - Lines: 1-145

- `css/shared/modals.css`: Modal dialog styling
  - Modal structure, animations
  - Lines: 1-64

- `css/shared/tabs.css`: Tab navigation components
  - Tab styling, active states
  - Lines: 1-41

- `css/shared/messages.css`: Alert and notification styles
  - Success, error, warning messages
  - Lines: 1-32

- `css/shared/autocomplete.css`: Autocomplete dropdown styling
  - Dropdown positioning, results styling
  ```css:patient_management/patient_records/static/css/shared/autocomplete.css
  startLine: 1
  endLine: 27
  ```

- `css/shared/navigation.css`: Navigation bar styling
  - Navigation links and user menu
  ```css:patient_management/patient_records/static/css/shared/navigation.css
  startLine: 1
  endLine: 20
  ```

- `css/shared/loading.css`: Loading indicators
  - Spinner animations and states
  ```css:patient_management/patient_records/static/css/shared/loading.css
  startLine: 1
  endLine: 13
  ```

- `css/shared/notes-modal.css`: Notes modal styling
  - Split-screen interface for note taking
  - Reference panel and tag management
  - Lines: 1-150

- `css/shared/split-layout.css`: Split-screen layout styling
  - Main content and notes sidebar layout
  - Responsive grid structure
  - Lines: 1-95

## JavaScript Functionality

### Core Features
- `js/patient_detail.js`: Patient record tab handling
  - Tab switching and content loading
  - Dynamic AJAX content updates
  - Collapsible card initialization
  - Pagination handling for all tab types (overview, clinical, medications, cmp_labs, cbc_labs, history)
  - Lines: 1-130

- `js/icd-autocomplete.js`: ICD code lookup
  - Autocomplete functionality for diagnosis codes
  - API integration for ICD code search
  - Result handling and selection
  ```javascript:icd-autocomplete.js
  startLine: 1
  endLine: 61
  ```

### Utils
- `js/utils/modal-manager.js`: Modal management utilities
  - Modal state management
  - Accessibility features (focus trap, keyboard navigation)
  - Loading states and content management
  ```javascript:modal-manager.js
  startLine: 1
  endLine: 137
  ```

- `js/utils/modal-utils.js`: Modal form handling utilities
  - Form submission and error handling
  - AJAX form processing
  - Success/error callback management
  ```javascript:patient_management/patient_records/static/js/utils/modal-utils.js
  startLine: 1
  endLine: 29
  ```

- `js/utils/date-input.js`: Date input handling
  - Default date setting
  - Keyboard shortcuts ('t' for today)
  - Future date validation for past-only fields
  ```javascript:date-input.js
  startLine: 1
  endLine: 32
  ```

- `js/phone-input.js`: Phone number formatting
  - Input masking and formatting
  - Real-time validation
  - Format: (XXX) XXX-XXXX
  ```javascript:phone-input.js
  startLine: 1
  endLine: 33
  ```

- `js/utils/notes-manager.js`: Patient notes management
  - Note creation and real-time updates
  - Reference attachment handling
  - Tag management system
  - Lines: 1-150

### Modals
- `js/modals/form-modal.js`: Form modal handling
  - Modal display and form submission
  - Collapsible card integration
  - Success/error handling
  ```javascript:form-modal.js
  startLine: 90
  endLine: 111
  ```

- `js/modals/confirmation-modal.js`: Confirmation dialogs
  - Delete confirmations
  - Action confirmations
  - Lines: 1-62

## Empty Files (Reserved)
- `css/pages/provider.css`: Reserved for provider-specific styles
- `css/pages/login.css`: Reserved for login page styles
- `css/shared/tables.css`: Reserved for table styling components

## Core Templates

- `templates/patient_records/base.html`: Base template with common structure
  - Core layout, CSS/JS includes, navigation
  - Lines: 1-75

- `templates/patient_records/base_form.html`: Base form template
  - Form structure and validation
  - Lines: 1-214

- `templates/patient_records/base_tabbed_form.html`: Tabbed form template
  - Tab navigation and content structure
  - Lines: 1-58

## Patient Management Templates

- `templates/patient_records/patient_list.html`: Patient listing page
  - Data table with patient information
  - Lines: 1-50

- `templates/patient_records/add_patient.html`: Add patient form
  - Patient information entry
  - Lines: 1-2

- `templates/patient_records/home.html`: Dashboard/home page
  - Quick links and navigation
  - Lines: 1-16

## Provider Management Templates

- `templates/patient_records/provider_list.html`: Provider listing page
  - Provider information table
  - Lines: 1-41

- `templates/patient_records/add_provider.html`: Add provider form
  - Provider information entry
  - Lines: 1-2

- `templates/patient_records/edit_provider.html`: Edit provider form
  - Provider information editing
  - Lines: 1-37

## Medical Record Templates

- `templates/patient_records/add_patient.html`: Add patient form
  - Patient information entry
  - Lines: 1-2

- `templates/patient_records/add_diagnosis.html`: Diagnosis entry form
  - ICD code lookup and diagnosis entry
  - Lines: 1-86

- `templates/patient_records/add_medications.html`: Medication entry form
  - Medication details and dosage
  - Lines: 1-2

- `templates/patient_records/add_vitals.html`: Vitals entry form
  - Patient vital signs recording
  - Lines: 1-2

- `templates/patient_records/add_labs.html`: Lab results entry form
  - Laboratory test results entry
  - Lines: 26-91

- `templates/patient_records/add_measurements.html`: Measurements entry form
  - Patient measurements recording
  - Lines: 1-2

- `templates/patient_records/add_symptoms.html`: Symptoms entry form
  - Patient symptoms recording
  - Lines: 1-3

- `templates/patient_records/add_occurence.html`: Add occurrence form
  - Form for recording patient occurrences
  - Lines: 1-3

## Component Templates

- `templates/components/_breadcrumbs.html`: Breadcrumb navigation
  - Page hierarchy navigation
  - Lines: 1-12

- `templates/components/_messages.html`: System messages
  - Success/error notifications
  - Lines: 1-7

- `templates/components/modal/_form_modal.html`: Modal form component
  - Reusable modal form structure
  - Lines: 1-12

- `templates/components/_navigation.html`: Main navigation bar
  - Referenced in base.html (line 28)

- `templates/components/_patient_header.html`: Patient header information
  - Referenced in base_form.html (line 7) and base_tabbed_form.html (line 7)

- `templates/components/_pagination.html`: Pagination controls
  - Referenced in multiple templates
  - Lines: 1-15

## Partial Templates

- `templates/patient_records/partials/_basic_info.html`: Basic patient information partial
  - Core patient demographic display
  - Lines: 1-16

- `templates/patient_records/partials/_form_field.html`: Form field rendering
  - Lines: 1-20

- `templates/patient_records/partials/_form_section.html`: Form section partial
  - Grouped form fields section
  - Lines: 1-14

- `templates/patient_records/partials/_medications.html`: Medications list partial
  - Current medications display
  - Lines: 1-45

- `templates/patient_records/partials/_overview.html`: Patient overview partial
  - Patient summary information
  - Lines: 1-66

- `templates/patient_records/partials/_history.html`: Patient history partial
  - Audit trail and history records with pagination
  - Collapsible history entries
  - Lines: 1-50

- `templates/patient_records/partials/_audit_trail.html`: Audit trail partial
  - Activity logging display
  - Lines: 1-22

- `templates/patient_records/partials/_clinical.html`: Clinical data display
  - Lines: 1-93

- `templates/patient_records/partials/_cmp_labs.html`: CMP Laboratory results display
  - Comprehensive Metabolic Panel results and pagination
  - Lines: 1-45

- `templates/patient_records/partials/_cbc_labs.html`: CBC Laboratory results display
  - Complete Blood Count results and pagination
  - Lines: 1-40

- `templates/patient_records/partials/_notes_list.html`: Patient notes listing
  - Displays list of patient notes with categories and attachments
  - Real-time updates via HTMX
  - Lines: 1-75

## Authentication Templates

- `templates/registration/login.html`: Login page
  - User authentication form
  - Lines: 1-34

## Form Templates

- `templates/patient_records/forms/edit_form.html`: Edit record form
  ```html:patient_management/patient_records/templates/patient_records/forms/edit_form.html
  startLine: 1
  endLine: 37
  ```

## Widget Templates

- `templates/widgets/phone_number.html`: Phone number input widget
  - Country code selector and input field
  - Lines: 1-22

## Template Tags

- `templates/patient_records/templatetags/__init__.py`: Initialization file for custom template tags
  - Required for loading custom template tags in Django
  - Lines: 1-1

- `templates/patient_records/templatetags/patient_tags.py`: Custom template tags for patient-related functionality
  - Includes tags for formatting patient data and other utilities
  - Lines: 1-50

- `templates/patient_records/templatetags/form_tags.py`: Custom template tags for form handling
  - Includes tags for rendering forms and form fields
  - Lines: 1-30

## Modal Templates

- `templates/components/modal/_form_modal.html`: Modal form component
  - Reusable modal form structure
  - Lines: 1-12

- `templates/components/modal/confirmation-modal.html`: Confirmation modal for actions
  - Used for delete confirmations and other critical actions
  - Lines: 1-15

- `templates/components/modal/error-modal.html`: Error modal display
  - Displays error messages to the user
  - Lines: 1-10

- `templates/components/modal/_notes_modal.html`: Patient notes modal
  - Split-screen note taking interface
  - Reference attachment panel
  - Real-time updates via HTMX
  - Lines: 1-85

## Models
- `patient_management/patient_records/models.py`: Database models for patient management
  - Defines models for Provider, Patient, Diagnosis, Visits, Vitals, CmpLabs, CbcLabs, Symptoms, Medications, Measurements, Imaging, Adls, Occurrences, RecordRequestLog, AuditTrail, ClinicalNotes, and PatientNote.
  - Lines: 1-300

## URLs
- `patient_management/patient_records/urls.py`: URL routing for patient-related views
  - Defines routes for home, patient management, clinical data entry, provider management, API endpoints, and patient notes management.
  - Lines: 1-30

- `patient_management/patient_management/urls.py`: Main URL configuration for the project
  - Includes admin routes and redirects to login.
  - Lines: 1-20 (or adjust based on actual line count)

## Settings
- `patient_management/patient_management/settings.py`: Project settings configuration
  - Contains settings for database, installed apps, middleware, logging, security, and CSP.
  - Lines: 1-80 (or adjust based on actual line count)