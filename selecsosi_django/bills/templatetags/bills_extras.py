from django import template
from ..models import Transaction

register = template.Library()



@register.filter(is_safe=True)
def transaction_type(value):
    for code, name in Transaction.TRANSACTION_CHOICES:
        if code == value:
            return name
