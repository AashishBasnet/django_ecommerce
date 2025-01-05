# your_app/templatetags/forms_extras.py
from django import template
import math
register = template.Library()


@register.filter
def add_class(field, css_class):
    """
    Adds the given CSS class to the field's widget.
    """
    return field.as_widget(attrs={'class': css_class})


@register.filter
def floor(value):
    """
    Floors a float value.
    """
    try:
        return math.floor(float(value))
    except (ValueError, TypeError):
        return value


@register.filter
def subtract(value, subtract_value):
    """
    Subtracts the second value from the first one.
    """
    try:
        return float(value) - float(subtract_value)
    except (ValueError, TypeError):
        return value


@register.filter
def in_range(value):
    return range(1, value + 1)
