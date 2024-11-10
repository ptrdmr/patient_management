from django import template

register = template.Library()

@register.filter
def get_form_field(form, field_name):
    """
    Template filter to get a form field by name
    Usage: {{ form|get_form_field:field_name }}
    """
    try:
        return form[field_name]
    except KeyError:
        return None

@register.filter
def get_field(form, field_name):
    try:
        return form[field_name]
    except KeyError:
        return None