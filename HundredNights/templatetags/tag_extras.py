
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
def visit_response_notes(responses):
    details = u"\n".join([u"{0}: {1}".format(r.question.title, r.details) for r in 
        responses.filter(details__isnull = False, bool_response__exact = True).exclude(details__exact=u'')])
    if details:
        return u"\n" + details
    else:
        return u""

@register.filter
def after_split_point(index, sequence):
    return index >= len(sequence) / 2.0

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
    
