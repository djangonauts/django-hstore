from django_hstore.fields import DictionaryField, ReferencesField
from django_hstore.managers import HStoreManager


try:
    from django_hstore.managers import HStoreGeoManager
except:
    # django.contrib.gis is not configured properly
    pass

import django
if django.get_version() < '1.7':
    from . import apps

