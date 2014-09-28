# -*- coding: utf-8 -*-

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from starmato.admin.models import get_starmato_option
from django.conf import settings


if 'django.contrib.staticfiles' in settings.INSTALLED_APPS:
    from django.contrib.staticfiles.templatetags.staticfiles import static
else:
    from django.templatetags.static import static

register = template.Library()

@register.simple_tag
def starmato_option(key):
    return get_starmato_option(key)


@register.simple_tag
def starmato_css():
    links = []

    for filename in [get_starmato_option("def_color") or "beige", get_starmato_option("def_iconset") or "blackcubes"]:
        links.append(mark_safe("<link rel='stylesheet' type='text/css' href='%s' />" % static("admin/css/"+filename+".css")))

    return u"\n".join(links)

@register.simple_tag
def starmato_branding():
    pic = get_starmato_option("project_logo")
    if len(pic):
        return mark_safe("<img src='%s' height='60px' />" % static(pic))
    for str in [get_starmato_option("project_name"), get_starmato_option("domain_name"), "StarMaTo<br />Administration"]:
        if len(str):
            return mark_safe(str)
