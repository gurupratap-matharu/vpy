from django import template


register = template.Library()


@register.filter
def gs_format(value):
    """
    Formats an integer or float with a dot thousand separator (e.g., 130000 -> 130.000).
    """
    if value is None or value == "":
        return ""
    try:
        # Convert to int to drop decimals, format with comma, then swap to dot
        number = int(float(value))
        return f"{number:,}".replace(",", ".")
    except (ValueError, TypeError):
        return value
