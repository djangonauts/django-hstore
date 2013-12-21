from django.db import models
from django.contrib.gis.db import models as geo_models
from django_hstore.query import HStoreQuerySet, HStoreGeoQuerySet


class HStoreManager(models.Manager):
    """
    Object manager which enables hstore features.
    """
    use_for_related_fields = True

    def get_query_set(self):
        return HStoreQuerySet(self.model, using=self._db)

    def hkeys(self, attr, **params):
        return self.filter(**params).hkeys(attr)

    def hpeek(self, attr, key, **params):
        return self.filter(**params).hpeek(attr, key)

    def hslice(self, attr, keys, **params):
        return self.filter(**params).hslice(attr, keys)


class HStoreGeoManager(geo_models.GeoManager, HStoreManager):
    """
    Object manager combining Geodjango and hstore.
    """
    def get_query_set(self):
        return HStoreGeoQuerySet(self.model, using=self._db)
