# -*- coding: utf-8 -*-

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

models_to_exclude = (
    'contact/contact/',
    'event/event/',
    'work/work/',
    'invoice/invoice/',
    'web/',
    'mailing/',
    'bookstore/',
)

# Do not show those models using the web filter
exclude_web_apps = (
    'web/projectsection/',
)

def model_exclude(applist, exclude):
    """
    Excludes all models specified in exclude variable from 
    the current applist.
    """
    newapplist = []
    for app in applist:
        newapp = {}
        newapp['app_url'] = app['app_url']
        newapp['name'] = app['name']
        newapp['has_module_perms'] = app['has_module_perms']
        newapp['models'] = []
        for model in app['models']:
            newapp['models'].append(model)
            for model_to_exclude in exclude:
                if model['admin_url'].find(model_to_exclude) != -1:
                    newapp['models'].remove(model)
        if len(newapp['models']) > 0:
            newapplist.append(newapp)
    return newapplist

@register.filter
def advanced(applist):
    return model_exclude(applist, models_to_exclude)

@register.filter
def web(applist):
    apps = []
    for app in applist:
        if app['app_url'] == 'web/' or app['app_url'] == 'bookstore/':
            apps.append(app)
    return model_exclude(apps, exclude_web_apps)

@register.filter
def mailing(applist):
    for app in applist:
        if app['app_url'] == 'mailing/':
            return [app,]
    return []
