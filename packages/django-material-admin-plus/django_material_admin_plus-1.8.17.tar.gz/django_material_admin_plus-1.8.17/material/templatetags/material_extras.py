from django import template

register = template.Library()

@register.filter
def length_is(value, arg):
    """
    Backwards\-compatible replacement for the removed `length_is` filter.
    Usage: {% if some_list|length_is:1 %}...{% endif %}
    """
    try:
        return len(value) == int(arg)
    except (TypeError, ValueError):
        return False
