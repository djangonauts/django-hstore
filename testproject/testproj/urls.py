from django.conf.urls import patterns, include, url

urlpatterns = patterns("",
    url(r"^$", "testapp.views.test_view", name="test"),
)
