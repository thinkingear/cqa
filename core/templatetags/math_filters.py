from django import template

register = template.Library()


@register.filter
def sub(value, arg):
    return value - arg


@register.filter
def mul(value, arg):
    return value * arg


@register.filter
def div(value, arg):
    try:
        return value / arg
    except (ValueError, ZeroDivisionError):
        return 0
