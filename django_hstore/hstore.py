from django_hstore.fields import DictionaryField, ReferencesField, SerializedDictionaryField  # noqa
from django_hstore.managers import HStoreManager  # noqa
from django_hstore.apps import GEODJANGO_INSTALLED


if GEODJANGO_INSTALLED:
    from django_hstore.managers import HStoreGeoManager  # noqa
