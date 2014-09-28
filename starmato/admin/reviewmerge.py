# -*- coding: utf-8 -*-
from itertools import chain
#
from django.forms.widgets import SelectMultiple
from django.forms.formsets import all_valid
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.admin.util import unquote, flatten_fieldsets, label_for_field
from django.contrib.admin import helpers
from django.db import transaction
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.template.response import TemplateResponse
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.html import escape
#
from starmato.admin.options import StarmatoModelAdmin

csrf_protect_m = method_decorator(csrf_protect)

class ReviewAndMergeSelectMultiple(SelectMultiple):
    def render_options(self, choices, selected_choices):
        # Normalize to strings.
        selected_choices = set(force_text(v) for v in selected_choices)
        output = []
        for option_value, option_label in chain(self.choices, choices):
            if isinstance(option_label, (list, tuple)):
                output.append(format_html('<optgroup label="{0}">', force_text(option_value)))
                for option in option_label:
                    if force_text(option) in selected_choices:
                        output.append(self.render_option(selected_choices, *option))
                output.append('</optgroup>')
            else:
                if force_text(option_value) in selected_choices:
                    output.append(self.render_option(selected_choices, option_value, option_label))
        return '\n'.join(output)

class   ReviewAndMergeAdmin(StarmatoModelAdmin):
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if "merge" in request.META["PATH_INFO"] and not 'widget' in kwargs:
            kwargs['widget'] = ReviewAndMergeSelectMultiple
        return super(ReviewAndMergeAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def get_urls(self):
        from django.conf.urls import patterns, url

        def wrap(view):
            from functools import update_wrapper
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        urlpatterns = super(ReviewAndMergeAdmin, self).get_urls()

        info = self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = patterns('',
            url(r'^(.+)/merge/$',
                wrap(self.merge_view),
                name='%s_%s_merge' % info),
        ) + urlpatterns

        return urlpatterns


    # This view is based on django.contrib.admin.options.ModelAdmin.change_view()
    # Edited/added parts are between STARTEDIT and ENDEDIT
    # Global idea is:
    # Handle request as a change_view with a added form to compare data.
    # STEP 1/  At first load, two forms are created. "old" and "modified".
    # "old" will be used for merging in javascript (IMPORTANT FOR STEP 2)
    # STEP 2a/ Validation. if "old" form (hand-made merge) is valid,
    # remove pending object from db and save edited model
    # STEP 2b/ If validation fails, display the two forms again
    @csrf_protect_m
    @transaction.atomic
    def merge_view(self, request, object_id, form_url='', extra_context=None):
        "The 'review_and_merge' admin view for this model."
        # STARTEDIT set merge template to default
        self.merge_template = None
        # ENDEDIT
        model = self.model
        opts = model._meta

        obj = self.get_object(request, unquote(object_id))

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_text(opts.verbose_name), 'key': escape(object_id)})

        # STARTEDIT Remove "_saveasnew" handler ENDEDIT

        ModelForm = self.get_form(request, obj)
        formsets = []
        inline_instances = self.get_inline_instances(request, obj)
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES, instance=obj)
            if form.is_valid():
                form_validated = True
                new_object = self.save_form(request, form, change=True)
            else:
                form_validated = False
                new_object = obj
            prefixes = {}
            for FormSet, inline in zip(self.get_formsets(request, new_object), inline_instances):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1 or not prefix:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(request.POST, request.FILES,
                                  instance=new_object, prefix=prefix,
                                  queryset=inline.get_queryset(request))

                formsets.append(formset)

            if all_valid(formsets) and form_validated:
                # STARTEDIT merging is valid, delete pending object
                pending = model.objects.get(pending_id=object_id)
                if pending.id != pending.pending_id:
                    obj_display = force_text(pending)
                    self.log_deletion(request, pending, obj_display)
                    self.delete_model(request, pending)
                else:
                    new_object.pending = None
                # ENDEDIT

                self.save_model(request, new_object, form, True)
                self.save_related(request, form, formsets, True)
                change_message = self.construct_change_message(request, form, formsets)
                self.log_change(request, new_object, change_message)

                # STARTEDIT redirect to change_view
                redirect_url = reverse('admin:%s_%s_change' %
                                       (opts.app_label, opts.model_name),
                                       args=(new_object.pk,),
                                       current_app=self.admin_site.name)
                preserved_filters = self.get_preserved_filters(request)
                redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
                return HttpResponseRedirect(redirect_url)
                # ENDEDIT redirect to change_view
        else:
            form = ModelForm(instance=obj)
            prefixes = {}
            for FormSet, inline in zip(self.get_formsets(request, obj), inline_instances):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1 or not prefix:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(instance=obj, prefix=prefix,
                                  queryset=inline.get_queryset(request))
                formsets.append(formset)

        adminForm = helpers.AdminForm(form, self.get_fieldsets(request, obj),
            self.get_prepopulated_fields(request, obj),
            self.get_readonly_fields(request, obj),
            model_admin=self)
        
        media = self.media + adminForm.media

        inline_admin_formsets = []
        for inline, formset in zip(inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request, obj))
            readonly = list(inline.get_readonly_fields(request, obj))
            prepopulated = dict(inline.get_prepopulated_fields(request, obj))
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset,
                fieldsets, prepopulated, readonly, model_admin=self)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media

        # STARTEDIT merging is not valid or the form was not submitted
        # create form with pending data
        obj2 = model.objects.get(pending_id=object_id)
        object2_id = obj2.id

        if not self.has_change_permission(request, obj2):
            raise PermissionDenied

        if obj2 is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_text(opts.verbose_name), 'key': escape(object2_id)})

        ModelForm = self.get_form(request, obj2)
        formsets2 = []
        inline_instances2 = self.get_inline_instances(request, obj2)
        form2 = ModelForm(instance=obj2)
        prefixes = {}
        for FormSet, inline in zip(self.get_formsets(request, obj2), inline_instances2):
            prefix = FormSet.get_default_prefix()
            prefixes[prefix] = prefixes.get(prefix, 0) + 1
            if prefixes[prefix] != 1 or not prefix:
                prefix = "%s-%s" % (prefix, prefixes[prefix])
            formset = FormSet(instance=obj2, prefix=prefix,
                              queryset=inline.get_queryset(request))
            formsets2.append(formset)

        adminForm2 = helpers.AdminForm(form2, self.get_fieldsets(request, obj2),
            self.get_prepopulated_fields(request, obj2),
            self.get_readonly_fields(request, obj2),
            model_admin=self)

        inline_admin_formsets2 = []
        for inline, formset in zip(inline_instances2, formsets2):
            fieldsets = list(inline.get_fieldsets(request, obj2))
            readonly = list(inline.get_readonly_fields(request, obj2))
            prepopulated = dict(inline.get_prepopulated_fields(request, obj2))
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset,
                fieldsets, prepopulated, readonly, model_admin=self)
            inline_admin_formsets2.append(inline_admin_formset)
        # ENDEDIT

        # STARTEDIT set context for this view
        context = {
            'title': _('Change %s') % force_text(opts.verbose_name),
            'adminform': adminForm,
            'adminform2': adminForm2,
            'object_id': object_id,
            'original': obj,
            'is_popup': False,
            'media': media,
            'inline_admin_formsets': inline_admin_formsets,
            'inline_admin_formsets2': inline_admin_formsets2,
            'errors': helpers.AdminErrorList(form, formsets),
            'app_label': opts.app_label,
            'preserved_filters': self.get_preserved_filters(request),

            'add': False,
            'change': True,
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request, obj),
            'has_delete_permission': self.has_delete_permission(request, obj),
            'has_file_field': True,  # FIXME - this should check if form or formsets have a FileField,
            'has_absolute_url': hasattr(self.model, 'get_absolute_url'),
            'form_url': form_url,
            'opts': opts,
            'content_type_id': ContentType.objects.get_for_model(self.model).id,
            'save_as': self.save_as,
            'save_on_top': self.save_on_top,
        }
        # ENDEDIT
        context.update(extra_context or {})
        

        return TemplateResponse(request, self.merge_template or [
            "admin/%s/%s/merge_form.html" % (opts.app_label, opts.model_name),
            "admin/%s/merge_form.html" % opts.app_label,
            "admin/merge_form.html"
        ], context, current_app=self.admin_site.name)

