from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def ru_plural(value, forms):
    """Русские формы множественного числа.

    Использование: {{ count|ru_plural:"отель,отеля,отелей" }}
    """
    try:
        n = int(value)
    except (TypeError, ValueError):
        return forms.split(",")[-1]

    forms = forms.split(",")
    n10 = n % 10
    n100 = n % 100
    if n10 == 1 and n100 != 11:
        return forms[0]
    if 2 <= n10 <= 4 and not (12 <= n100 <= 14):
        return forms[1]
    return forms[2] if len(forms) > 2 else forms[1]
