# -*- coding: utf-8 -*-
import os
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.shortcuts import redirect
#
from starmato.admin.models import StarmatoOption, starmato_options
from starmato.admin.sites import site

################################################################################
# Test the exitence of StarmatoOptions and display a warning message if any
# of them is missing
################################################################################
def index(request):
    for option_name in starmato_options:
        try:
            option = StarmatoOption.objects.get(option=option_name)
        except:
            messages.error(request, _(u'An important option (%s) is missing from your configuration. The software could get unstable. Please reset this option or contact your administrator.' % option_name))

    if not site.has_permission(request):
        return site.login(request)
    else:
        return site.index(request)

################################################################################
# Add a restart button to force the restart of the wsgi service
# Useful when an StarmatoOption has been changed (they are not load
# dynamically for efficiency)
################################################################################
@permission_required('is_superuser')
def wsgi_restart(request):
    os.system('touch django.wsgi')
    messages.info(request, _(u'The software has been restarted.'))
    return redirect('admin:index')

#Le rédemarrage du serveur a été effectué















from django.core.urlresolvers import RegexURLPattern, RegexURLResolver
from django.conf.urls import patterns
from django.utils.decorators import available_attrs
from django.utils import translation

try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.4 fallback.

class DecoratedURLPattern(RegexURLPattern):
    def resolve(self, *args, **kwargs):
        result = RegexURLPattern.resolve(self, *args, **kwargs)
        if result:
#            result = list(result)
            result.func = self._decorate_with(result.func)
#            result[0] = self._decorate_with(result[0])
        return result

def recurse_decoration(patterns, func):
    for p in patterns:
        if isinstance(p, RegexURLResolver):
            recurse_decoration(p.url_patterns, func)
        if isinstance(p, RegexURLPattern):
            p.__class__ = DecoratedURLPattern
            p._decorate_with = func

def decorated_patterns(prefix, func, *args):
    result = patterns(prefix, *args)
    if func:
        recurse_decoration(result, func) 
    return result

def force_translation(func):
    def inner(request, *args, **kwargs):
        translation.activate('fr-FR')
        return func(request, *args, **kwargs)
    return inner
