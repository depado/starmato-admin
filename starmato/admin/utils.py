# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.templatetags.l10n import localize
import locale
#
def     model_to_list(model, fields=['id', 'label'], empty_value=False):
    l = []
    if empty_value:
        l.append(('0', '------'))

    cleanfields = []
    for f in fields:
        cleanfields.append("`%s`" % f)

    objs = list(model.objects.raw('SELECT %s FROM %s_%s' % (",".join(cleanfields), model._meta.app_label, model._meta.module_name)))

    if model._meta.ordering:
        for order in model._meta.ordering:
            if order in fields:
                objs.sort(key=lambda item:eval("item.%s" % order))

    try:
        for obj in objs:
            l.append((u'%d' % getattr(obj, fields[0]), getattr(obj, fields[1])))
    except:
        pass
    return l

def     model_to_array(model):
    l = {}
    objs = model.objects.all()

    for obj in objs:
        l[u"%d" % obj.id] = unicode(obj)
    return l

def link_related(related, label=None):
    url = reverse('admin:%s_%s_change' % (related._meta.app_label, related._meta.module_name), args = [related.id])
    if label == None:
        label = unicode(related)
    return mark_safe('<a href="%s">%s</a>' % (url, label))

def clever_round(dec):
    if int(dec) == dec:
        return format(dec, ".0f")
    else:
        return format(dec, ".2f")
