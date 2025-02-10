from django import template

register = template.Library()

@register.filter
def full_name(patient):
    """Returns the patient's full name in a consistent format"""
    return f"{patient.last_name or 'Unknown'}, {patient.first_name or 'Unknown'}"
