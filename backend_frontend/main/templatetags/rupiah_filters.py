from django import template

register = template.Library()

@register.filter(name='rupiah')
def rupiah(value):
    try:
        val = float(value)
        
        formatted = "{:,.2f}".format(val)
        
        formatted = formatted.replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")
        
        return f"Rp{formatted}"
        
    except (ValueError, TypeError):
        return "Rp0,00"