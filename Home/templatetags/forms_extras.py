# your_app/templatetags/forms_extras.py
from django import template

register = template.Library()

@register.filter
def add_class(field, css_class):
    """
    Adds the given CSS class to the field's widget.
    """
    return field.as_widget(attrs={'class': css_class})
