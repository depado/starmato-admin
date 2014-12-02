# -*- coding: utf-8 -*-
from itertools import chain
#
from django import forms
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
#
from django.conf import settings


class HiddenFilteredSelectMultiple(FilteredSelectMultiple):
    """
    A Filtered SelectMultiple with a short view.

    """
    class Media:
        js = (settings.MEDIA_URL + "admin/js/SelectFilterHide.js", )

    def render(self, name, value, attrs=None, choices=()):
        output = [u'<input type="text" class="auto_select" id="auto_%s" readonly />' % name]
        output.append(u'<input type="button" value="%s" id="show_%s" onClick="ShowFilteredSelectMultiple(this);" />' 
                      % (_('Change'), name))
        output.append(u'<div class="hidden" class="man_select" id="man_%s">' % name)
        output.append(super(HiddenFilteredSelectMultiple, self).render(name, value, attrs, choices))
        output.append(u'</div>')
        return mark_safe(u''.join(output))

####################################################################################################
# Hack to get categories in FilteredSelectMultiple (does not work natively because choices list 
# is altered between __init__ and render)
# django.contrib.admin SelectBox.js is overridden by starmato.admin to handle optgroup
####################################################################################################
class CategorizedFilteredSelectMultiple(FilteredSelectMultiple):
    class Media:
        js = (settings.MEDIA_URL + "admin/js/core.js",
              settings.MEDIA_URL + "admin/js/SelectBox.js",
              settings.MEDIA_URL + "admin/js/addevent.js",
              settings.MEDIA_URL + "admin/js/SelectFilter2.js")

    def __init__(self, verbose_name, is_stacked, attrs=None, choices=()):
        self._choices = choices
        super(CategorizedFilteredSelectMultiple, self).__init__(verbose_name, is_stacked, attrs, choices)

    def render(self, name, value, attrs=None, choices=()):
        self.choices = self._choices
        return super(CategorizedFilteredSelectMultiple, self).render(name, value, attrs, choices)




####################################################################################################
# Hack to get categories in CheckboxSelectMultiple (two levels)
####################################################################################################
class CategorizedCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    class Media:
        js = (settings.MEDIA_URL + "admin/js/Checkbox2.js", )

    def __init__(self, attrs=None, choices=()):
        super(CategorizedCheckboxSelectMultiple, self).__init__(attrs)
        self.group_choices = choices

    def rendercb(self, final_attrs, name, option_value, option_label, label_for, str_values):
        cb = forms.CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
        option_value = force_unicode(option_value)
        rendered_cb = cb.render(name, option_value)
        option_label = conditional_escape(force_unicode(option_label))
        return u'<li><label%s>%s %s</label></li>' % (label_for, rendered_cb, option_label)

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        option_attrs = self.build_attrs(attrs, name=name)
        output = [u'<ul>']
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        group_attrs = dict(option_attrs, name=name+"-group", onChange="categorized_checkbox_multiple_change(this);")
        i = 0
        for tok1, tok2 in self.group_choices:
            # each choice can be [<anytype>value, <unicode>label] (case 1)
            # or [<unicode>group, <iterable>choices] (case 2)
            if type(tok2) == unicode:
                option_value = tok1
                option_label = tok2
                options = []
                if has_id:
                    final_attrs = dict(option_attrs, id='%s_%s' % (attrs['id'], i))
                    label_for = u' for="%s"' % final_attrs['id']
                else:
                    label_for = ''
                i = i + 1
                output.append(self.rendercb(final_attrs, name, option_value, option_label, '', str_values))
            else:
                option_value = "0"
                option_label = tok1
                options = tok2
                final_attrs = group_attrs
                output.append(self.rendercb(final_attrs, name+"-group", option_value, option_label, '', str_values))
                output.append(u'<ul class="indent1">')
                # only for case 2
                for option_value, option_label in options:
                    if has_id:
                        final_attrs = dict(option_attrs, id='%s_%s' % (attrs['id'], i))
                        label_for = u' for="%s"' % final_attrs['id']
                    else:
                        label_for = ''
                    i = i + 1
                    output.append(self.rendercb(final_attrs, name, option_value, option_label, label_for, str_values))

                output.append(u'</ul>')
        output.append(u'</ul>')
        return mark_safe(u'\n'.join(output))



def categorized_choices(model, group_model, attname=None):
    for field in model._meta.fields:
        if field.rel != None and type(field.rel.to()) == group_model:
            attname = field.get_attname()
            break

    if attname == None:
        raise TypeError("Cannot group '%s' using '%s': relationship not found" %
                        (model._meta.object_name, group_model._meta.object_name))

    
    final_list = []

    for instance in model.objects.extra(where=["%s IS NULL" % attname]):
        final_list.append([instance.pk, unicode(instance)])

    for group in group_model.objects.all():
        sub_list = []
        for instance in model.objects.extra(where=["%s=%d" % (attname, group.pk)]):
            sub_list.append([instance.pk, unicode(instance)])
        final_list.append([unicode(group), sub_list])

    return final_list
