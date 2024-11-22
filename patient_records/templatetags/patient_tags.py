from django import template

register = template.Library()

@register.filter
def full_name(patient):
    """Returns the patient's full name in a consistent format"""
    if patient.middle_name:
        return f"{patient.last_name}, {patient.first_name} {patient.middle_name}"
    return f"{patient.last_name}, {patient.first_name}"
