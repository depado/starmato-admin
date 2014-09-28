# -*- coding: utf-8 -*-

from django.contrib.admin import site
from django import template
from django.http import HttpRequest
from django.template.defaultfilters import stringfilter
from django.db.models import Q
from django.db.models.sql.query import get_order_dir
from django.contrib.admin.views.main import ChangeList
from django.http import QueryDict
from django.core.urlresolvers import reverse
#

################################################################################
# WARNING : the list of ordering fields MUST be a UNIQUE COMBINATION
# (best at MySQL level or at model validation)
# for the template tag to WORK PROPERLY
################################################################################

register = template.Library()

def get_query_set(context, item):
    request = HttpRequest()
    preserved_filters = ""
    if 'preserved_filters' in context:
        preserved_filters = context['preserved_filters']
        tmp = QueryDict(preserved_filters)
        request.GET = QueryDict(tmp.get("_changelist_filters"))
    model = type(item)
    adm = site._registry[model]
    cl = ChangeList(request, model, [], [],
                    [], [], adm.search_fields, [],
                    '0', [], [], adm)

#    cl = ChangeList(request, type(item), [], [], [], [], adm.search_fields, [], "0", [], [], adm)
    return cl.get_query_set(request), preserved_filters

def get_next_or_previous(item, qs, filters, next):
    if next:
        default_ordering = 'ASC'
    else:
        default_ordering = 'DESC'

    # First, determine the ordering. This code is from get_ordering() in
    # django.db.sql.compiler
    if qs.query.extra_order_by:
        ordering = qs.query.extra_order_by
    elif not qs.query.default_ordering:
        ordering = qs.query.order_by
    else:
        ordering = qs.query.order_by or qs.query.model._meta.ordering

    assert not ordering == '?', 'This makes no sense for random ordering.'

    for field in ordering:
        query_filter = None
        if field[0] == '-':
            item_value = getattr(item, field[1:])
        else:
            item_value = getattr(item, field)

        if item_value is None:
            continue

        # Account for possible reverse ordering
        field, direction = get_order_dir(field, default_ordering)

        # Either make sure we filter increased values or lesser values
        # depending on the sort order
        if direction == 'ASC':
            filter_dict = {'%s__gt' % field: item_value}
        else:
            filter_dict = {'%s__lt' % field: item_value}

        # Make sure we nicely or the conditions for the queryset
        query_filter = Q(**filter_dict)
        if query_filter is not None:
            qs = qs.filter(query_filter)

    # Reverse the order if we're looking for previous items
    l = list(qs)
    pos = 0
    if default_ordering == 'DESC' and len(l) > 0:
        pos = len(l)-1
        ref = l[pos]
        while pos > 0: 
            alldiff = True
            for field in ordering:
                if field[0] == '-':
                    field = field[1:]
                alldiff = alldiff and getattr(l[pos-1], field) != getattr(ref, field)
            if alldiff == True:
                break
            pos -= 1

    # Return either the next/previous item or None if not existent
    try:
        info = (item._meta.app_label, item._meta.object_name.lower())
        url = reverse('admin:%s_%s_change' % info, args=(l[pos].pk,))
        return url+"?"+filters
    except IndexError:
        return None


def get_previous(context, item):
    qs, filters = get_query_set(context, item)
    return get_next_or_previous(item, qs, filters, False)

def get_next(context, item):
    qs, filters = get_query_set(context, item)
    return get_next_or_previous(item, qs, filters, True)

def get_previous_and_next(context, item):
    qs, filters = get_query_set(context, item)
    return (get_next_or_previous(item, qs, filters, False), get_next_or_previous(item, qs, filters, True))

#  <a href="{% url change_url object.pk %}">
#    <span class="content-title object-button">
#      <img src='{% static "admin/images/big_icon_{{ forloop.counter }}.gif" %}' />
#    </span>
#  </a>
