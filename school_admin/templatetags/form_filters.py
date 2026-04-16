from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def add_class(field, css_class):
    """Add CSS classes to form field"""
    if hasattr(field, 'as_widget'):
        return field.as_widget(attrs={"class": css_class})
    return field
