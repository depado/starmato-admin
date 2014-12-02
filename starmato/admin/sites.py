from django.views.decorators.cache import never_cache
from django.contrib import admin
from django.utils.text import capfirst
from django.core.urlresolvers import reverse


class AdminSite(admin.AdminSite):

    def __init__(self, name='admin', app_name='admin'):
        super(AdminSite, self).__init__(name, app_name)
        self._main_models = []
        self._main_models_extras = {}

    def register(self, model_or_iterable, admin_class=None, **options):
        super(AdminSite, self).register(model_or_iterable, admin_class, options=options)
        if "main" in options and options["main"] == True:
            name = capfirst(model_or_iterable._meta.verbose_name_plural)
            self._main_models.append(name)
            if "extra_indexes" in options:
                self._main_models_extras[name] = options["extra_indexes"]
        admin.site.register(model_or_iterable, admin_class, **options)

    def unregister(self, model_or_iterable):
        model = capfirst(model_or_iterable._meta.verbose_name_plural)
        if model in self._main_models:
            self._main_models.remove(model)
        admin.site.unregister(model_or_iterable)
        try:
            super(AdminSite, self).unregister(model_or_iterable)
        except:
            pass

    @never_cache
    def index(self, request, extra_context=None):
        tr = super(AdminSite, self).index(request, extra_context)
        main_models = []
        for app in tr.context_data["app_list"]:
            for model in app["models"]:
                if model["name"] in self._main_models:
                    if model["name"] in self._main_models_extras:
                        model["extras"] = self._main_models_extras[model["name"]]
                        for extra in model["extras"]:
                            if "model" in extra and extra["model"] is not None:
                                info = (extra["model"]._meta.app_label, extra["model"]._meta.object_name.lower())
                                extra["url"] = reverse('admin:%s_%s_changelist' % info)

                    main_models.append(model)
        tr.context_data["main_models"] = main_models
        return tr

site = AdminSite()
