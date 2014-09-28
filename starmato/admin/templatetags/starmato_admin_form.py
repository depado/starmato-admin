# -*- coding: utf-8 -*-
from django import template
from django.contrib.admin.models import LogEntry
from django.utils.safestring import mark_safe

from starmato.admin.templatetags._get_previous_or_next import *
from starmato.admin.templatetags._fieldset_related import *
from starmato.admin.templatetags._logs import *

register = template.Library()

# register filters from get_previous_or_next
#register.filter('get_previous', get_previous)
#register.filter('get_next', get_next)
#register.filter('get_previous_and_next', get_previous_and_next)

#register.simple_tag(takes_context=True)(get_previous_and_next)

register.assignment_tag(takes_context=True)(get_previous_and_next)
register.assignment_tag(takes_context=True)(get_previous)
register.assignment_tag(takes_context=True)(get_next)

# register filters from fieldset_related
register.filter('before_related', before_related)
register.filter('after_related', after_related)

# register filters from logs
register.filter('logs', logs)



class RequestTestNode(template.Node):
    def __init__(self,):
        self.request = template.Variable('request')
        print self.request
    def render(self, context):
        rqst = self.request.resolve(context)
        return "The URL is: %s" % rqst.get_full_path()
