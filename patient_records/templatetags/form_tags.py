from django import template

register = template.Library()

@register.filter
def get_field(form, field_name):
    """
    Custom template filter to get a form field by name
    Usage in template: {{ form|get_field:field_name }}
    """
    return form[field_name]