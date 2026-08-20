from django import template

register = template.Library()


@register.filter
def to_range(value, max_options=20):
    """Turn a stock count into range(1, value+1) for use in a
    {% for %} loop, so quantity dropdowns never offer more units than
    are actually in stock. Capped so a product with huge stock doesn't
    render a giant dropdown."""

    try:
        value = int(value)
    except (TypeError, ValueError):
        return range(0)
    return range(1, min(value, max_options) + 1)
