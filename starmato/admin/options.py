# -*- coding: utf-8 -*-
from sys import maxint
from datetime import date
from tinymce.widgets import TinyMCE
#
import copy
from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper, FilteredSelectMultiple
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, QueryDict
from django.utils.http import urlencode
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from functools import update_wrapper
from django.utils.safestring import mark_safe
from django.contrib.admin.util import unquote, flatten_fieldsets, label_for_field
from django.contrib.contenttypes.models import ContentType
#
from django.core.exceptions import ValidationError
from django.core.urlresolvers import NoReverseMatch
from django.core.validators import EMPTY_VALUES
#
from django.conf import settings

################################################################################
# Predefines TinyMCE widgets using a "mode" argument
# - full: all available TinyMCE options
# - oneline: 40px height TinyMCE and light options
# - <default>: default tinyMCE with moderate amount of options
################################################################################
class StarmatoTinyMCE(TinyMCE):
    def __init__(self, mode="", attrs={'cols': 80, 'rows': 15}):
         if mode == "full":
              mce_attrs={'width': 600, 
                         'height': 450,
                         'theme': 'advanced',
                         'theme_advanced_font_sizes': "10pt,11pt,12pt,13pt,14pt,15pt,16pt,17pt,18pt,19pt,20pt,21pt,22pt,23pt,24pt",
                         'font_size_style_values': "10pt,11pt,12pt,13pt,14pt,15pt,16pt,17pt,18pt,19pt,20pt,21pt,22pt,23pt,24pt",
                         'plugins' : "autolink,spellchecker,style,layer,table,advhr,advimage,advlink,emotions,inlinepopups,media,contextmenu,paste,directionality,noneditable,visualchars,nonbreaking,xhtmlxtras,template,lineheight",
                         'theme_advanced_buttons1' : "bold,italic,underline,strikethrough,|,sub,sup,|,forecolor,backcolor,|,justifyleft,justifycenter,justifyright,justifyfull,|,lineheight,fontselect,fontsizeselect",
                         'theme_advanced_buttons2' : "link,unlink,image,removeformat,cleanup,code,|,charmap,emotions,|,spellchecker,visualchars,hr,|,tablecontrols"
                         }
         elif mode == "oneline":
              mce_attrs={'width': 400,
                         'height': 40, # Smaller as possible.
                         'theme': 'advanced',
                         'theme_advanced_buttons1': 'code, bold, italic, underline, strikethrough, separator, sub, sup, separator, undo, redo, cleanup, separator, link, unlink',
                         'theme_advanced_buttons2': '',
                         'theme_advanced_buttons3': ''
                         }
         else:
              mce_attrs={'width': 600, 
                         'height': 450,
                         'theme': 'advanced',
                         'theme_advanced_buttons1': 'code, bold, italic, underline, strikethrough, separator, justifyleft, justifycenter, justifyright, justifyfull, separator, sub, sup, separator, undo, redo, cleanup, separator, link, unlink',
#                         'theme_advanced_buttons1': 'code, fontsizeselect, bold, italic, underline, strikethrough, separator, justifyleft, justifycenter, justifyright, justifyfull, separator, sub, sup, separator, undo, redo, cleanup, separator, bullist, numlist, separator, link, unlink',
                         'theme_advanced_buttons2': '',
                         'theme_advanced_buttons3': ''
                         }

         super(StarmatoTinyMCE, self).__init__(mce_attrs=mce_attrs, attrs=attrs)

################################################################################
# CRAZY hack to get personal add icon for related field
# In fact can be much more interesting to get a custom wrapper
################################################################################
class   StarmatoRelatedFieldWidgetWrapper(RelatedFieldWidgetWrapper):
    def __init__(self, widget):
        super(StarmatoRelatedFieldWidgetWrapper, self).__init__(widget.widget, widget.rel, widget.admin_site, widget.can_add_related)

    def render(self, name, value, *args, **kwargs):
        rel_to = self.rel.to
        info = (rel_to._meta.app_label, rel_to._meta.object_name.lower())
        try:
            related_url = reverse('admin:%s_%s_add' % info, current_app=self.admin_site.name)
        except:
            self.can_add_related = False
        self.widget.choices = self.choices
        output = [self.widget.render(name, value, *args, **kwargs)]
        if self.can_add_related:
            # TODO: "id_" is hard-coded here. This should instead use the 
            # correct API to determine the ID dynamically.
            output.append(u'<a href="%s" class="add-another" id="add_id_%s" onclick="return showAddAnotherPopup(this);"> ' % \
                (related_url, name))
            output.append(u'<img src="%(static)s/admin/images/icon_addlink.gif" width="10" height="10" title="%(info)s" alt="%(info)s"/></a>' % {'static': settings.STATIC_URL, 'info': _('Add Another')})
        return mark_safe(u''.join(output))

# action_rows is a list to add rows of action buttons to the change_form view
# structure is :
# {"id": ", // identifier to manipulate content. Also used in html 
#  "class": "", // additional css classes (space separated string)
#  'actions": [ // list of buttons
#           "value": "" // value to display on the button (string or unicode)
#           "url": "" // url to call
# Here is the example for the starmato.pdf.options.StarmatoPDFAdmin
#    action_rows = [
#        {"id": "StarMaToPrint",
#         "class": "print-row",
#         "actions": [
#                {"value": _(u"Print"), 
#                 "url": "print/"},
#                ]
#         },
#        ]
class ActionRows(object):
    action_rows = []

    def addActionRow(self, uid, actions=[], css_class="", safe=False):
        for action_row in self.action_rows:
            if action_row["id"] == uid:
                if safe==False:
                    raise ValueError, "'%s' is already registered in the list of actionRows" % uid
                else:
                    return

        self.action_rows.append({"id": uid,
                             "class": css_class,
                             "actions": actions,
                             })
        
    def addActionToRow(self, uid, value, url, safe=False):
        for action_row in self.action_rows:
            if action_row["id"] == uid:
                for action in action_row["actions"]:
                    if action["value"] == value:
                        if safe == False:
                            raise ValueError, "'%s/%s' is already registered in the list of actions" % (uid, value)
                        else:
                            return
                action_row["actions"].append({"value": value, "url": url})
                return
                
        raise ValueError, "'%s' is not register in the list of actionRows" % uid

################################################################################
# Special ModelAdmin
# Dynamic inlines
# Copy url
# Archive url
# Change list action when nothing is selected
################################################################################
class StarmatoModelAdmin(admin.ModelAdmin, ActionRows):
    exclude_from_copy = ()
    save_on_top = True

    class Media:
        js = (settings.MEDIA_URL+'admin/js/Popups.js',
              settings.MEDIA_URL+'admin/js/ChangeForm.js',
              settings.MEDIA_URL+'admin/js/SelectBox.js',)

    # set two different type of inlines (see admin.py for more)
    # static_inlines are always visible
    # contextual_inlines are displayed according to some rules defined in get_formsets
    def __init__(self, model, admin_site):
        if hasattr(self, 'static_inlines'):
            for ci in self.static_inlines:
                if not ci in self.inlines:
                    self.inlines += (ci,)

        if (hasattr(self, 'contextual_inlines')):
            for context in self.contextual_inlines:
                for ci in context[1]['inlines']:
                    if not ci in self.inlines:
                        self.inlines += (ci,)

        super(StarmatoModelAdmin, self).__init__(model, admin_site)

    # hack to set readonly users and groups
    # TODO: check this
    def get_readonly_fields(self, request, obj=None):
        readonly = super(StarmatoModelAdmin,self).get_readonly_fields(request, obj)
        return readonly
        if not request.user.is_superuser:
            # Prevent a staff user from editing anything of a superuser.
            for fieldset in flatten_fieldsets(self.declared_fieldsets):
                try:
                    label_for_field(fieldset, type(obj), self)
                    readonly.append(fieldset)
                except:
                    pass
        return readonly


    # Visible Inlines depends on the contextual inlines
    # May be overridden
    def get_inline_instances(self, request, obj=None):
        # build the list of hidden inlines
        # 1. get the whole set of inlines
        hidden_inlines = []
        if hasattr(self, 'contextual_inlines'):
            hidden_inlines = list(self.inlines)

        # 2. remove from the hidden list the static inlines (always visible)
        if hasattr(self, 'static_inlines'):
            for show_inline in self.static_inlines:
                 if show_inline in hidden_inlines:
                      hidden_inlines.remove(show_inline)

        # 3. check condition for contextual inlines
        if len(hidden_inlines) and obj is not None:
            for toshow in self.contextual_inlines:
                if eval('obj.%s' % toshow[0]) == toshow[1]['value']:
                    for show_inline in toshow[1]['inlines']:
                        hidden_inlines.remove(show_inline)

        # 4. get inline instances and set the showTab parameter
        # Note: noTab is used for TabTabularInline
        inline_instances = super(StarmatoModelAdmin, self).get_inline_instances(request, obj)
        for inline in inline_instances:
            if (type(inline) in hidden_inlines) or inline.noTab:
                inline.showTab = False
            else:
                inline.showTab = True
        return inline_instances

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if not 'widget' in kwargs:
            kwargs['widget'] = FilteredSelectMultiple(db_field.name, is_stacked = False)
        return super(StarmatoModelAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    # Add urls to archive objects
    def get_urls(self):
        from django.conf.urls import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = patterns('',
            url(r'^(.+)/archive/$',
                wrap(self.archive_view),
                name='%s_%s_archive' % info),
        )

        return urlpatterns + super(StarmatoModelAdmin, self).get_urls()

    # Add view to archive objects
    def archive_view(self, request, object_id, extra_context=None):
        opts = self.model._meta
        obj = self.get_object(request, unquote(object_id))
        pk_value = obj._get_pk_val()
        
        msg = _('The %(name)s "%(obj)s" was archived successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj)}

        obj.archive = True
        obj.save()
        self.message_user(request, msg)
        if self.has_change_permission(request, None):
            post_url = '../../'
        else:
            post_url = '../../../'
        return HttpResponseRedirect(post_url)

    # TODO: why is this here?
    def post_copy(self, original, new):
        pass

    # If post_url_save is given, redirect
    def response_add(self, request, obj, post_url_continue=None):
        if "post_url_save" in request.POST and len(request.POST['post_url_save']):
            return HttpResponseRedirect(request.POST['post_url_save'])
        return super(StarmatoModelAdmin, self).response_add(request, obj, post_url_continue)

    # Add view to duplicate objects using the change view with a special
    # POST parameter (_copy)
    def response_change(self, request, obj):
        if "post_url_save" in request.POST and len(request.POST['post_url_save']):
            return HttpResponseRedirect(request.POST['post_url_save'])
        if "_copy" in request.POST:
            opts = obj._meta

            # Handle proxy models automatically created by .only() or .defer()
            verbose_name = opts.verbose_name
            if obj._deferred:
                opts_ = opts.proxy_for_model._meta
                verbose_name = opts_.verbose_name

            msg = _('The %(name)s "%(obj)s" was duplicated successfully.') % {'name': force_unicode(verbose_name), 'obj': force_unicode(obj)}

            new = copy.deepcopy(obj)
            new.pk = new.id = None
            self.post_copy(obj, new)
            new.save()
            for rel in opts.get_all_related_objects():
                if rel.var_name not in self.exclude_from_copy:
                    instances = rel.model.objects.complex_filter({"%s" % rel.field.name: obj})
                    for instance in instances:
                        instance._set_pk_val(None)
                        setattr(instance, rel.field.name, new)
                        instance.save()

            self.message_user(request, msg + ' ' + _("You may edit the duplicated record below."))
            if "_popup" in request.POST:
                post_url_continue += "?_popup=1"
            return HttpResponseRedirect(post_url_continue % new._get_pk_val())

        return super(StarmatoModelAdmin, self).response_change(request, obj)

    # Related field wrapper with personal icon and tinyMCE for text fields
    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(StarmatoModelAdmin, self).formfield_for_dbfield(db_field, **kwargs)

        if formfield and type(formfield.widget) == RelatedFieldWidgetWrapper:
            formfield.widget = StarmatoRelatedFieldWidgetWrapper(formfield.widget)
        return formfield

    def get_row_css(self, obj, index):
        return ''

################################################################################
# Use special templates for inlines
################################################################################
class   AEPFForm(forms.ModelForm):
    class Meta:
        widgets = {
            'label': forms.TextInput(attrs={'size': 12}),
            'number': forms.TextInput(attrs={'size': 24}),
            'zip': forms.TextInput(attrs={'size': 12}),
            }

class   TabTabularInline(admin.TabularInline):
    inMainBloc = False
    template = 'admin/edit_inline/tabtabular.html'
    extra = 1
    showTab = True
    noTab = False
    can_add = True
    activate = None

    # Related field wrapper with personal icon
    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(TabTabularInline, self).formfield_for_dbfield(db_field, **kwargs)
        if formfield and type(formfield.widget) == RelatedFieldWidgetWrapper:
            formfield.widget = StarmatoRelatedFieldWidgetWrapper(formfield.widget)
        return formfield

class   MainBlocInline(admin.TabularInline):
    inMainBloc = True
    showTab = True
    noTab = False
    extra = 0
    can_add = True
    template = 'admin/edit_inline/mainbloc.html'
    form = AEPFForm

    def get_formset(self, request, obj=None, **kwargs):
        fs = super(MainBlocInline, self).get_formset(request, obj, **kwargs)
        if eval("len(self.model.objects.filter(%s=obj))" % fs.fk.name) == 0:
           self.extra = 1
           fs = super(MainBlocInline, self).get_formset(request, obj, **kwargs)
        return fs

    # Related field wrapper with personal icon
    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(MainBlocInline, self).formfield_for_dbfield(db_field, **kwargs)
        if formfield and type(formfield.widget) == RelatedFieldWidgetWrapper:
            formfield.widget = StarmatoRelatedFieldWidgetWrapper(formfield.widget)
        return formfield

################################################################################
# Empty ForeignKey: required but filled by js
# 1) Empty form
#    queryset is set to none() in formfield so no request is made 
#    to build the form
#    real_queryset is set to the "real" queryset for validation
# 2) Fill the field
#    the field is then set by js scripts
# 3) Validation
#    "real" queryset is hit during validation (to_python)
#
# To use, insert EmptyForeignKey, EmptyOneToOneField and EmptyManyToManyField
# in a model.
################################################################################
from django.db import models
from django.forms import ModelChoiceField
from django.forms.widgets import Select

################################################################################
# Override widgets.Select to display the list of choices with an empty queryset 
# Used as EmptyForeignKeyFormField default widget
################################################################################
class   EmptySelect(Select):
    def __init__(self, queryset, to_field_name):
        super(EmptySelect, self).__init__()
        self.to_field_name = to_field_name
        self.real_queryset = queryset

    def render(self, name, value, attrs=None, choices=()):
        if value is not None and value != '':
            key = self.to_field_name or 'pk'
            choices = ((value, force_unicode(self.real_queryset.get(**{key:value}))),)

        return super(EmptySelect, self).render(name, value, attrs, choices)

################################################################################
# Override forms.ModelChoiceField to create an empty queryset at load but
# validate against the "real" queryset 
################################################################################
class   EmptyForeignKeyFormField(forms.ModelChoiceField):
    def __init__(self, queryset, empty_label=u"---------", cache_choices=False,
                 required=True, widget=None, label=None, initial=None,
                 help_text=None, to_field_name=None, real_queryset=None, *args, **kwargs):
        self.real_queryset = real_queryset
        super(EmptyForeignKeyFormField, self).__init__(queryset.none(), empty_label, cache_choices,
                                                       required, widget, label, initial,
                                                       help_text, to_field_name, *args, **kwargs)
        if widget == None:
            self.widget = EmptySelect(real_queryset, to_field_name)

    def to_python(self, value):
        if value in EMPTY_VALUES:
            return None
        try:
            key = self.to_field_name or 'pk'
            value = self.real_queryset.get(**{key: value})
            return value
        except:
            return None

    def validate(self, value):
         if value is not None:
              try:
                   key = self.to_field_name or 'pk'
                   value = self.real_queryset.get(**{key: getattr(value, key)})
              except (ValueError, self.queryset.model.DoesNotExist):
                   raise ValidationError(self.error_messages['invalid_choice'])

################################################################################
# Override forms.ModelMultipleChoiceField to create an empty queryset at load 
# but clean using the "real" queryset 
################################################################################
class   EmptyMultipleChoiceField(forms.ModelMultipleChoiceField):
    def clean(self, value):
        empty_qs = self.queryset
        self.queryset = self.real_queryset
        output = super(EmptyMultipleChoiceField, self).clean(value)
        self.queryset = empty_qs
        return output


################################################################################
# Defines an EmptyForeignKey for models (form class and two querysets)
################################################################################
class   EmptyForeignKey(models.ForeignKey):
    def formfield(self, **kwargs):
        db = kwargs.pop('using', None)
        defaults = {
            'form_class': EmptyForeignKeyFormField,
            'queryset': self.rel.to._default_manager.using(db).none(),
            'real_queryset': self.rel.to._default_manager.using(db).complex_filter(self.rel.limit_choices_to)        
            }
        defaults.update(kwargs)
        return super(EmptyForeignKey, self).formfield(**defaults)

################################################################################
# Defines an EmptyOneToOneField for models (form class and two querysets)
################################################################################
class   EmptyOneToOneField(models.OneToOneField):
    def formfield(self, **kwargs):
        db = kwargs.pop('using', None)
        defaults = {
            'form_class': EmptyForeignKeyFormField,
            'queryset': self.rel.to._default_manager.using(db).none(),
            'real_queryset': self.rel.to._default_manager.using(db).complex_filter(self.rel.limit_choices_to)
        }
        defaults.update(kwargs)
        return super(EmptyOneToOneField, self).formfield(**defaults)

################################################################################
# Defines an EmptyManyToMany for models (form class and two querysets)
################################################################################
class   EmptyManyToManyField(models.ManyToManyField):
    def formfield(self, **kwargs):
        db = kwargs.pop('using', None)
        defaults = {
            'form_class': EmptyMultipleChoiceField,
            'queryset': self.rel.to._default_manager.using(db).none(),
        }
        defaults.update(kwargs)
        form_field = super(EmptyManyToManyField, self).formfield(**defaults)
        form_field.real_queryset = self.rel.to._default_manager.using(db).complex_filter(self.rel.limit_choices_to)
        return form_field




################################################################################
# Autocomplete TextInput: no force selection, no foreign key
# Uses autocomplete
################################################################################
#from django.db import models
#from django.forms.widgets import TextInput, Textarea
#from django.utils.safestring import mark_safe
#
#class   ACTextInput(TextInput):
#    source = ''
#    class Media:
#        css = {
#            'all': (settings.AUTOCOMPLETE_MEDIA_PREFIX+'/css/jquery-ui.css',),
#            }
#        js = (settings.AUTOCOMPLETE_MEDIA_PREFIX+'/js/jquery-ui.js', settings.AUTOCOMPLETE_MEDIA_PREFIX+'/js/jquery_autocomplete.js',)
#
#    def __init__(self, attrs=None):
#        self.source = attrs.pop('source', '')
#        super(ACTextInput, self).__init__(attrs)
#
#    def render(self, name, value, attrs=None):
#        output = super(ACTextInput, self).render(name, value, attrs)
#        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
#        script = u"".join(["<script id='", final_attrs['id'].replace('label', 'script'),
#                          "' type='text/javascript'>django.autocomplete('#", final_attrs['id'],
#                          "', { 'source': '", self.source, "', ",
#                          "'multiple': false, 'force_selection': false});</script>"])
#        return mark_safe(output+script)
#
#class   ACTextarea(Textarea):
#    source = ''
#    class Media:
#        css = {
#            'all': (AUTOCOMPLETE_MEDIA_PREFIX+'/css/jquery-ui.css',),
#            }
#        js = (AUTOCOMPLETE_MEDIA_PREFIX+'/js/jquery-ui.js', AUTOCOMPLETE_MEDIA_PREFIX+'/js/jquery_autocomplete.js',)
#
#    def __init__(self, attrs=None):
#        self.source = attrs.pop('source', '')
#        super(ACTextarea, self).__init__(attrs)
#
#    def render(self, name, value, attrs=None):
#        output = super(ACTextarea, self).render(name, value, attrs)
#        final_attrs = self.build_attrs(attrs, name=name)
#        script = u"".join(["<script id='", final_attrs['id'].replace('label', 'script'),
#                          "' type='text/javascript'>django.autocomplete('#", final_attrs['id'],
#                          "', { 'source': '", self.source, "', ",
#                          "'multiple': true, 'force_selection': false});</script>"])
#        return mark_safe(output+script)
#
#class   ACCharField(models.CharField):
#    source = ''
#    size = 37
#    def __init__(self, *args, **kwargs):
#        self.source = kwargs.pop('source', '')
#        self.size = kwargs.pop('size', 37)
#        super(ACCharField, self).__init__(*args, **kwargs)
#
#    def formfield(self, *args, **kwargs):
#        defaults = {}
#        defaults.update(kwargs)
#        defaults.update({'widget': ACTextInput(attrs={'size': self.size, 'source': self.source})})
#        return super(ACCharField, self).formfield(**defaults)

from starmato.admin.reviewmerge import ReviewAndMergeAdmin 
