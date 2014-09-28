# -*- coding: utf-8 -*-

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

from django.conf import settings

@register.filter
@stringfilter
def verbose(value):
    value = value.lower()
    try:
        index = [i[0] for i in settings.APP_VERBOSE_LABELS].index(value)
        return settings.APP_VERBOSE_LABELS[index][1].decode('utf-8')
    except:
        return value

@register.filter
def error_count(errors):
    e = 0
    for error in errors:
        e += len(error)
    return e

@register.filter
@stringfilter
def short(string, length):
    if len(string) < length:
        return string
    tokens = string.split(' ')
    tokens.reverse()
    output = tokens.pop()
    while len(tokens) and len(output+tokens[0]) < length:
        output += " "+tokens.pop()
    return output + "..."

@register.filter
@stringfilter
def stupid_filter(string, stupid):
    return string.replace(stupid, '<br />')

@register.simple_tag
def index(array, i):
    return array[i]
