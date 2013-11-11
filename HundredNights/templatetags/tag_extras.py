
from django import template
import calendar
import locale

register = template.Library()

@register.filter
def currency(dollars):
    if not dollars:
        return ""
    locale.setlocale(locale.LC_ALL, '')
    return locale.currency(float(dollars), grouping=True)

@register.filter
def bool_yn(bool_val):
    if bool_val:
        return "Yes"
    else:
        return "No"

@register.filter
def replace_none(val, replacement):
    if val:
        return val
    else:
        return replacement
        

@register.filter
def tabindex(value, index):
    """ Add a tabindex attribute to the widget for a bound field. """
    value.field.widget.attrs['tabindex'] = index
    return value

@register.filter
def toticks(d):
    """ Convert a date to Unix time """
    return calendar.timegm(d.timetuple())
    
