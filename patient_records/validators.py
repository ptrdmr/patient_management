from abc import ABC, abstractmethod
from typing import Dict, Any, List
from django.core.exceptions import ValidationError
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class BaseValidator(ABC):
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> List[str]:
        """Validate the data and return list of error messages"""
        pass

class ModelValidator(BaseValidator):
    """Validates data against model constraints"""
    
    def validate(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        
        # Required fields validation
        required_fields = ['patient', 'date', 'symptom', 'source', 'person_reporting']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"{field} is required")
        
        # Field length validation
        if len(data.get('symptom', '')) > 200:
            errors.append("Symptom description cannot exceed 200 characters")
        
        if len(data.get('source', '')) > 100:
            errors.append("Source cannot exceed 100 characters")
            
        if len(data.get('person_reporting', '')) > 200:
            errors.append("Person reporting cannot exceed 200 characters")
        
        return errors

class BusinessRuleValidator(BaseValidator):
    """Validates data against business rules"""
    
    def validate(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        
        # Date validation
        if data.get('date'):
            if data['date'] > timezone.now().date():
                errors.append("Date cannot be in the future")
        
        # Severity validation
        severity = data.get('severity')
        if severity is not None:
            if not isinstance(severity, int) or severity < 1 or severity > 5:
                errors.append("Severity must be between 1 and 5")
        
        # Provider validation
        provider = data.get('provider')
        if provider:
            if not hasattr(provider, 'id'):
                errors.append("Invalid provider reference")
        
        return errors

class IntegrityValidator(BaseValidator):
    """Validates data integrity and relationships"""
    
    def validate(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        
        # Patient existence validation
        patient = data.get('patient')
        if patient:
            if not hasattr(patient, 'id'):
                errors.append("Invalid patient reference")
        
        # Data consistency validation
        if data.get('notes') and len(data['notes'].strip()) == 0:
            errors.append("Notes cannot be only whitespace")
        
        if data.get('symptom') and len(data['symptom'].strip()) == 0:
            errors.append("Symptom cannot be only whitespace")
        
        return errors

class ValidationPipeline:
    """Orchestrates the validation process"""
    
    def __init__(self):
        self.validators = [
            ModelValidator(),
            BusinessRuleValidator(),
            IntegrityValidator()
        ]
    
    def validate(self, data: Dict[str, Any]) -> List[str]:
        """Run all validators and return combined error messages"""
        all_errors = []
        
        try:
            for validator in self.validators:
                errors = validator.validate(data)
                all_errors.extend(errors)
        except Exception as e:
            logger.error(f"Error during validation: {str(e)}")
            all_errors.append(f"Validation error: {str(e)}")
        
        return all_errors

# Data transformation utilities
def sanitize_text(text: str) -> str:
    """Clean and sanitize text input"""
    if not text:
        return ""
    return text.strip()

def normalize_severity(severity: Any) -> int:
    """Normalize severity value to integer"""
    if isinstance(severity, str):
        try:
            severity = int(severity)
        except ValueError:
            return None
    return severity if isinstance(severity, int) and 1 <= severity <= 5 else None

def format_date(date: Any) -> str:
    """Format date to ISO format"""
    if hasattr(date, 'isoformat'):
        return date.isoformat()
    return str(date)

# Create singleton instance
validator = ValidationPipeline() 