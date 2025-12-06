from django import template

register = template.Library()

@register.filter(name='rupiah')
def rupiah(value):
    try:
        return f"Rp {int(value):,}".replace(",", ".")
    except (ValueError, TypeError):
        return value