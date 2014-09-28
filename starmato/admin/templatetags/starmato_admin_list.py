# -*- coding: utf-8 -*-

from django import template
from django.contrib.admin.views.main import PAGE_VAR
from django.utils.safestring import mark_safe
from django.utils.html import escape

register = template.Library()

@register.simple_tag
def     paginator_direct(cl):
    js = "location.href='%s&%s='+Math.min(%d, Math.max(0, (parseInt($('#page_direct').val())-1)))" % (escape(cl.get_query_string()), PAGE_VAR, cl.paginator.num_pages)

    return mark_safe(u'<input type="text" id="page_direct" value="1" /> <input type="button" value="Go" onClick="%s">' % js)


@register.simple_tag
def row_css(cl, index):
    if not hasattr(cl.model_admin, 'get_row_css'):
        return u''
    return cl.model_admin.get_row_css(cl.result_list[index], index)
