## Django Project Analysis and Implementation Request

### Project Context
I'm working on a Django-based patient records management system with HTML, CSS, and JavaScript frontend. The project follows standard Django architecture and best practices, featuring comprehensive patient data management, medical measurements tracking, and audit logging.

### Files to Review
Please analyze the following components of my Django project:
- Project settings (settings.py)
- URL configurations (urls.py files)
- Models (models.py files)
- Views (views.py files)
- Templates (*.html files)
- Static files (CSS, JavaScript)
- Forms (forms.py files)
- Project-specific middleware
- Any custom management commands
- Test files

### Project-Specific Components
1. Form Categories
   - Patient Registration
   - Vital Signs (BP, temp, SPO2, pulse, respirations)
   - Activities of Daily Living (ADLs)
   - Medications
   - Lab Results (CMP)
   - Imaging Results

2. Medical Data Validation
   - Vital signs ranges (documented in BaseForm)
   - Date validations
   - Contact information formats
   - Required medical fields

3. Patient Record Structure
   - Demographics and contact info
   - Power of Attorney details
   - Medical history (allergies, code status)
   - Visit records
   - Measurements tracking

4. Audit and History
   - Change tracking
   - User action logging
   - Patient history views
   - Record modification trails

5. UI Framework
   - Sectioned form layout
   - Patient header component
   - Breadcrumb navigation
   - Form error handling
   - AJAX form submissions

### Current Request
[INSERT YOUR SPECIFIC REQUEST HERE]

### Implementation Requirements
When implementing changes:
1. Maintain existing functionality and avoid breaking changes
2. Follow Django best practices and coding standards
3. Ensure backward compatibility where possible
4. Consider security implications of any changes
5. Preserve existing user permissions and authentication systems
6. Maintain current database relationships and data integrity
7. Preserve medical data validation rules
8. Maintain audit trail functionality

### Required Checks
Before implementing changes, please:
1. Review all related model relationships
2. Check URL pattern conflicts
3. Verify template inheritance chains
4. Assess impact on existing views and API endpoints
5. Review database migrations impact
6. Check static file dependencies
7. Verify middleware compatibility
8. Consider caching implications
9. Review authentication/authorization requirements
10. Verify medical data validation rules
11. Check audit trail implications

### Expected Output
Please provide:
1. List of files that need modification
2. Detailed explanation of proposed changes
3. Any new files that need to be created
4. Required migration steps
5. Potential risks and mitigation strategies
6. Testing recommendations
7. Rollback plan if needed

### Additional Considerations
- Performance impact
- Scalability implications
- Browser compatibility
- Mobile responsiveness
- Medical data validation
- Patient data privacy
- Audit trail requirements
- Form section organization
- UI component consistency

### Implementation Format
For each file that needs changes, please provide:
```python
# File: [filename]
# Location: [file path]

[code changes with clear comments]
```

### Post-Implementation Steps
1. List of required tests
2. Migration commands
3. Static file collection requirements
4. Cache clearing instructions
5. Server restart requirements
6. Audit trail verification
7. Medical data validation checks

Note: Please highlight any assumptions made or additional information needed to complete the request.