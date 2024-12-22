# Activities of Daily Living

## Overview
The Activities of Daily Living (ADL) module tracks and manages patient functional status and daily activities assessment.

## Core Features

### ADL Assessment
```python
class ADLAssessment(models.Model):
    """Model for tracking ADL assessments."""
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    assessed_by = models.ForeignKey('Staff', on_delete=models.PROTECT)
    assessment_date = models.DateTimeField(auto_now_add=True)
    
    # Basic ADLs
    bathing = models.IntegerField(
        choices=[
            (0, 'Dependent'),
            (1, 'Needs Assistance'),
            (2, 'Independent')
        ]
    )
    dressing = models.IntegerField(
        choices=[
            (0, 'Dependent'),
            (1, 'Needs Assistance'),
            (2, 'Independent')
        ]
    )
    toileting = models.IntegerField(
        choices=[
            (0, 'Dependent'),
            (1, 'Needs Assistance'),
            (2, 'Independent')
        ]
    )
    transferring = models.IntegerField(
        choices=[
            (0, 'Dependent'),
            (1, 'Needs Assistance'),
            (2, 'Independent')
        ]
    )
    continence = models.IntegerField(
        choices=[
            (0, 'Incontinent'),
            (1, 'Occasional Accident'),
            (2, 'Continent')
        ]
    )
    feeding = models.IntegerField(
        choices=[
            (0, 'Dependent'),
            (1, 'Needs Assistance'),
            (2, 'Independent')
        ]
    )
    
    # Additional notes
    notes = models.TextField(blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['patient', 'assessment_date']),
        ]
```

## Assessment Tools

### Barthel Index Calculator
```python
def calculate_barthel_index(assessment):
    """Calculate Barthel Index score from ADL assessment."""
    scores = {
        'bathing': assessment.bathing * 5,
        'dressing': assessment.dressing * 5,
        'toileting': assessment.toileting * 5,
        'transferring': assessment.transferring * 7.5,
        'continence': assessment.continence * 5,
        'feeding': assessment.feeding * 5
    }
    
    total_score = sum(scores.values())
    
    return {
        'total_score': total_score,
        'category_scores': scores,
        'independence_level': get_independence_level(total_score)
    }

def get_independence_level(score):
    """Determine independence level based on Barthel Index score."""
    if score >= 80:
        return 'Independent'
    elif score >= 60:
        return 'Slightly Dependent'
    elif score >= 40:
        return 'Moderately Dependent'
    else:
        return 'Severely Dependent'
```

## Progress Tracking

### ADL Progress Report
```python
def generate_adl_progress_report(patient_id, start_date, end_date):
    """Generate ADL progress report for specified period."""
    assessments = ADLAssessment.objects.filter(
        patient_id=patient_id,
        assessment_date__range=(start_date, end_date)
    ).order_by('assessment_date')
    
    progress_data = {
        'assessments': [],
        'trend_analysis': {}
    }
    
    for assessment in assessments:
        barthel_score = calculate_barthel_index(assessment)
        progress_data['assessments'].append({
            'date': assessment.assessment_date,
            'barthel_score': barthel_score['total_score'],
            'independence_level': barthel_score['independence_level']
        })
    
    progress_data['trend_analysis'] = analyze_adl_trends(assessments)
    return progress_data

def analyze_adl_trends(assessments):
    """Analyze trends in ADL assessments."""
    categories = ['bathing', 'dressing', 'toileting', 
                 'transferring', 'continence', 'feeding']
    
    trends = {}
    for category in categories:
        scores = [getattr(assessment, category) 
                 for assessment in assessments]
        trends[category] = {
            'improvement': calculate_improvement(scores),
            'current_status': scores[-1] if scores else None,
            'history': scores
        }
    
    return trends
```

## Care Planning

### ADL Care Plan
```python
class ADLCarePlan(models.Model):
    """Model for ADL-specific care planning."""
    assessment = models.ForeignKey('ADLAssessment', on_delete=models.CASCADE)
    created_by = models.ForeignKey('Staff', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    review_date = models.DateField()
    
    # Care plan details
    goals = models.TextField()
    interventions = models.TextField()
    equipment_needs = models.TextField(blank=True)
    
    # Progress tracking
    progress_notes = models.ManyToOneRel(
        'ADLProgressNote',
        on_delete=models.CASCADE,
        related_name='care_plan'
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['assessment', 'review_date']),
        ]

class ADLProgressNote(models.Model):
    """Model for tracking progress on ADL care plan."""
    care_plan = models.ForeignKey('ADLCarePlan', on_delete=models.CASCADE)
    noted_by = models.ForeignKey('Staff', on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)
    note = models.TextField()
    progress_status = models.CharField(
        max_length=20,
        choices=[
            ('IMPROVING', 'Improving'),
            ('MAINTAINING', 'Maintaining'),
            ('DECLINING', 'Declining')
        ]
    )
```

## Related Documentation
- [[Patient Records & Demographics]]
- [[Clinical Information Management]]
- [[Care Planning]]
- [[Progress Notes]]

## Tags
#adl #functional-status #patient-care #assessment 