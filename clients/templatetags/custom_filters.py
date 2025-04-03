from django import template
from datetime import datetime, date

register = template.Library()

@register.filter
def current_year(value=None):
    return datetime.now().year


@register.filter
def generate_range(value):
    try:
        return range(int(value))
    except (ValueError, TypeError):
        return []
    
@register.filter
def date_difference(due_date):
    return (date.today() - due_date).days if due_date < date.today() else 0
