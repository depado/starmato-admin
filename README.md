# The `admin` module

The `admin` module provides all the basic but extra behaviour in django administration
to get the starmato main functions.

It includes:

- specific admin actions
- filters and templatetags
- middleware functions
- dynamic handle of inlines
- advanced display options for `change_view`
- a search form for change list
- and more...

## Quick Start

1. Add `starmato.admin` to your settings like this:

        INSTALLED_APPS = (
            ...
            'django.contrib.admin',
            'starmato.admin',
        )

2. In development mode, set up `TEMPLATE_DIRS` and `STATICFILES_DIRS` explicitly:

        TEMPLATE_DIRS = (
            ...
            '/path/to/starmato/admin/templates/',
        )

        STATICFILES_DIRS = (
            ...
            '/path/to/starmato/admin/media/',
        )

    then collect all static files with:

        $ python manage.py collectstatic

3. Add urls patterns like this (add `starmato.admin` before `contrib.admin.site.urls` to
get StarMaTo admin pages`:

        import starmato
        from django.contrib import admin
        admin.autodiscover()

        urlpatterns = patterns('',
            ...
            url(r'^admin/', include(starmato.admin)),
            url(r'^admin/', include(admin.site.urls)),
        )

4. Import fixtures if required. Available fixtures are `country.json`, `currency.json`, `language.json`, and `options.json`:

        $ python manage.py syncdb
        $ python manage.py loaddata <path_to_starmato_json_fixtures>
 
5. Create your models as usual in `models.py`:

        class MyModel(models.Model):
            txt = models.CharField(max_length=12)


6. Register your models using StarMaTo site in `admin.py`:

        from myapp.models import MyModel
        from starmato.admin.sites import site

        site.register(MyModel, main=True)

    kwargs `main` is important to define which are the most important models to display as blocs 
    in index.html.

7. Use other options, like searchform :

        class MyAdmin(StarmatoModelAdmin):
	    searchform_fields = ("field1", "field2")