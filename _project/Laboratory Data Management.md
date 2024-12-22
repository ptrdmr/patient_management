# Laboratory Data Management

## Overview
This document details the laboratory data management system, including test ordering, result tracking, and reporting functionality.

## Lab Data Models

### Lab Order
```python
class LabOrder(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    ordering_provider = models.ForeignKey('Provider', on_delete=models.SET_NULL, null=True)
    ordered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    
    class Meta:
        ordering = ['-ordered_at']
```

### Lab Results
```python
class LabResult(models.Model):
    order = models.ForeignKey(LabOrder, on_delete=models.CASCADE)
    test_name = models.CharField(max_length=100)
    result_value = models.CharField(max_length=50)
    unit = models.CharField(max_length=20)
    reference_range = models.CharField(max_length=50)
    is_abnormal = models.BooleanField(default=False)
    resulted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-resulted_at']
```

## Lab Test Types

### Complete Blood Count (CBC)
```python
class CbcResult(LabResult):
    wbc = models.DecimalField(max_digits=5, decimal_places=2)
    rbc = models.DecimalField(max_digits=5, decimal_places=2)
    hemoglobin = models.DecimalField(max_digits=5, decimal_places=2)
    hematocrit = models.DecimalField(max_digits=5, decimal_places=2)
    platelets = models.IntegerField()
```

### Comprehensive Metabolic Panel (CMP)
```python
class CmpResult(LabResult):
    sodium = models.IntegerField()
    potassium = models.DecimalField(max_digits=4, decimal_places=1)
    chloride = models.IntegerField()
    co2 = models.IntegerField()
    glucose = models.IntegerField()
    bun = models.IntegerField()
    creatinine = models.DecimalField(max_digits=4, decimal_places=2)
```

## Lab Order Workflow

### Order Creation
1. Select patient
2. Choose test type(s)
3. Set priority
4. Add clinical information
5. Submit order

### Result Processing
1. Receive lab results
2. Validate data
3. Flag abnormal values
4. Store results
5. Notify providers

## Result Analysis

### Reference Range Checking
```python
def check_reference_range(result_value, test_type):
    """Check if result is within reference range"""
    ranges = REFERENCE_RANGES.get(test_type, {})
    if not ranges:
        return None
        
    low = ranges.get('low')
    high = ranges.get('high')
    
    if low is not None and result_value < low:
        return 'LOW'
    if high is not None and result_value > high:
        return 'HIGH'
    return 'NORMAL'
```

### Critical Value Alerts
```python
def check_critical_values(result):
    """Check for critical lab values"""
    critical_ranges = CRITICAL_VALUES.get(result.test_name, {})
    if not critical_ranges:
        return False
        
    value = float(result.result_value)
    if value <= critical_ranges.get('critical_low', float('-inf')):
        return 'CRITICAL LOW'
    if value >= critical_ranges.get('critical_high', float('inf')):
        return 'CRITICAL HIGH'
    return None
```

## Result Reporting

### Report Generation
```python
def generate_lab_report(order):
    """Generate formatted lab report"""
    results = order.labresult_set.all()
    report_data = {
        'patient': order.patient,
        'order_date': order.ordered_at,
        'results': results,
        'abnormal_flags': [r for r in results if r.is_abnormal],
        'provider': order.ordering_provider
    }
    return report_data
```

### Result Trending
- Historical result comparison
- Trend visualization
- Delta checking
- Result graphing

## Quality Control

### Data Validation
- Result range checking
- Unit verification
- Completeness validation
- Duplicate detection

### Quality Metrics
- Turnaround time
- Critical value reporting
- Order completion rate
- Result accuracy

## Integration

### Lab System Interface
```python
class LabInterface:
    def send_order(self, order):
        """Send order to lab system"""
        pass
        
    def receive_results(self, results):
        """Process incoming results"""
        pass
```

### Result Notifications
- Provider alerts
- Critical value calls
- Result availability
- Order status updates

## Related Documentation
- [[Lab Order Guide]]
- [[Result Interpretation]]
- [[Critical Values]]
- [[Lab Integration]]

## Tags
#laboratory #lab-results #clinical-data #testing 