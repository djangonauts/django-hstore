from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',  # noqa
    url(r'^admin/', include(admin.site.urls)),
)


if 'grappelli' in settings.INSTALLED_APPS:
    urlpatterns = urlpatterns + patterns('',  # noqa
        url(r'^grappelli/', include('grappelli.urls')),
    )
