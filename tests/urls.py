from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)


if 'grappelli' in settings.INSTALLED_APPS:
    urlpatterns = urlpatterns + patterns('',
        url(r'^grappelli/', include('grappelli.urls')),
    )