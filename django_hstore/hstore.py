from django_hstore.fields import DictionaryField, ReferencesField, SerializedDictionaryField  # noqa
from django_hstore.managers import HStoreManager  # noqa


try:
    from django_hstore.managers import HStoreGeoManager  # noqa
except:
    # django.contrib.gis is not configured properly
    pass

import django
if django.get_version() < '1.7':
    from . import apps  # noqa

