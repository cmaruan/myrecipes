from django import template

register = template.Library()


@register.filter
def keyvalue(d, key):
    if type(d) == dict:
        return d.get(key, '')
    return ''