# Medical Imaging Records

## Overview
The Medical Imaging Records module manages patient imaging studies, results, and DICOM integration.

## Core Features

### Imaging Study Management
```python
class ImagingStudy(models.Model):
    """Model for tracking imaging studies."""
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    ordered_by = models.ForeignKey(
        'Provider',
        related_name='ordered_studies',
        on_delete=models.PROTECT
    )
    performed_by = models.ForeignKey(
        'Provider',
        related_name='performed_studies',
        on_delete=models.PROTECT,
        null=True
    )
    
    # Study details
    study_type = models.CharField(
        max_length=50,
        choices=[
            ('XRAY', 'X-Ray'),
            ('CT', 'CT Scan'),
            ('MRI', 'MRI'),
            ('US', 'Ultrasound'),
            ('NM', 'Nuclear Medicine')
        ]
    )
    body_site = models.CharField(max_length=100)
    reason = models.TextField()
    urgency = models.CharField(
        max_length=20,
        choices=[
            ('STAT', 'Immediate'),
            ('URGENT', 'Within 24 hours'),
            ('ROUTINE', 'Routine')
        ],
        default='ROUTINE'
    )
    
    # Scheduling
    ordered_date = models.DateTimeField(auto_now_add=True)
    scheduled_date = models.DateTimeField(null=True)
    performed_date = models.DateTimeField(null=True)
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=[
            ('ORDERED', 'Ordered'),
            ('SCHEDULED', 'Scheduled'),
            ('IN_PROGRESS', 'In Progress'),
            ('COMPLETED', 'Completed'),
            ('CANCELLED', 'Cancelled')
        ],
        default='ORDERED'
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['patient', 'ordered_date']),
            models.Index(fields=['status', 'scheduled_date']),
        ]
```

### DICOM Integration
```python
class DICOMStudy(models.Model):
    """Model for DICOM study metadata."""
    imaging_study = models.OneToOneField(
        'ImagingStudy',
        on_delete=models.CASCADE
    )
    study_instance_uid = models.CharField(max_length=64, unique=True)
    accession_number = models.CharField(max_length=16, unique=True)
    study_date = models.DateField()
    study_time = models.TimeField()
    study_description = models.CharField(max_length=64)
    
    # DICOM metadata
    modality = models.CharField(max_length=16)
    manufacturer = models.CharField(max_length=64, null=True)
    institution_name = models.CharField(max_length=64, null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['study_instance_uid']),
            models.Index(fields=['accession_number']),
        ]

class DICOMSeries(models.Model):
    """Model for DICOM series metadata."""
    study = models.ForeignKey('DICOMStudy', on_delete=models.CASCADE)
    series_instance_uid = models.CharField(max_length=64, unique=True)
    series_number = models.IntegerField()
    series_description = models.CharField(max_length=64)
    modality = models.CharField(max_length=16)
    body_part_examined = models.CharField(max_length=16)
    
    class Meta:
        indexes = [
            models.Index(fields=['series_instance_uid']),
            models.Index(fields=['study', 'series_number']),
        ]
```

## Image Storage

### PACS Integration
```python
class PACSConfiguration(models.Model):
    """Configuration for PACS integration."""
    name = models.CharField(max_length=100)
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    ae_title = models.CharField(max_length=16)
    enabled = models.BooleanField(default=True)

def store_dicom_image(dicom_file, study_instance_uid):
    """Store DICOM image in PACS system."""
    pacs_config = PACSConfiguration.objects.filter(enabled=True).first()
    
    if not pacs_config:
        raise ValueError("No PACS configuration available")
    
    # PACS connection details
    pacs = {
        'host': pacs_config.host,
        'port': pacs_config.port,
        'ae_title': pacs_config.ae_title
    }
    
    # Store image using DICOM protocol
    try:
        with DicomConnection(pacs) as conn:
            conn.store_file(dicom_file)
            return True
    except Exception as e:
        logger.error(f"PACS storage error: {e}")
        return False
```

## Reporting

### Radiology Report
```python
class RadiologyReport(models.Model):
    """Model for radiology reports."""
    imaging_study = models.OneToOneField(
        'ImagingStudy',
        on_delete=models.CASCADE
    )
    radiologist = models.ForeignKey(
        'Provider',
        on_delete=models.PROTECT
    )
    report_date = models.DateTimeField(auto_now_add=True)
    
    # Report sections
    clinical_history = models.TextField()
    technique = models.TextField()
    findings = models.TextField()
    impression = models.TextField()
    recommendations = models.TextField(blank=True)
    
    # Report status
    status = models.CharField(
        max_length=20,
        choices=[
            ('DRAFT', 'Draft'),
            ('PRELIMINARY', 'Preliminary'),
            ('FINAL', 'Final'),
            ('AMENDED', 'Amended')
        ]
    )
    finalized_date = models.DateTimeField(null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['imaging_study', 'report_date']),
            models.Index(fields=['status', 'finalized_date']),
        ]
```

## Image Viewing

### DICOM Viewer Integration
```javascript
class DicomViewer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.cornerstone = cornerstone;
        this.cornerstoneTools = cornerstoneTools;
    }
    
    async loadStudy(studyInstanceUid) {
        // Initialize viewer
        this.cornerstone.enable(this.container);
        
        // Load study metadata
        const study = await this.loadStudyMetadata(studyInstanceUid);
        
        // Load first series
        if (study.series.length > 0) {
            await this.loadSeries(study.series[0].seriesInstanceUid);
        }
        
        // Enable tools
        this.enableViewerTools();
    }
    
    enableViewerTools() {
        // Enable standard tools
        this.cornerstoneTools.addTool(WindowLevelTool);
        this.cornerstoneTools.addTool(PanTool);
        this.cornerstoneTools.addTool(ZoomTool);
        this.cornerstoneTools.addTool(LengthTool);
        
        // Set active tools
        this.cornerstoneTools.setToolActive('WindowLevel', { mouseButtonMask: 1 });
        this.cornerstoneTools.setToolActive('Pan', { mouseButtonMask: 2 });
        this.cornerstoneTools.setToolActive('Zoom', { mouseButtonMask: 4 });
    }
}
```

## Related Documentation
- [[Patient Records & Demographics]]
- [[Clinical Information Management]]
- [[API Reference]]
- [[PACS Integration]]

## Tags
#imaging #radiology #dicom #pacs 