__import__('pkg_resources').declare_namespace(__name__)

from django.conf.urls import url

from starmato.admin.views import decorated_patterns, force_translation

urlpatterns = decorated_patterns('', force_translation, 
    # Url to restart site
    url(r'^wsgi_restart/$', 'starmato.admin.views.wsgi_restart'),
    url(r'^$', 'starmato.admin.views.index'),
)
