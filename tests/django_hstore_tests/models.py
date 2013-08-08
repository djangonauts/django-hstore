from django.db import models
from django.contrib.gis.db import models as geomodels
from django_hstore import hstore


class Ref(models.Model):
    name = models.CharField(max_length=32)


class HStoreModel(models.Model):
    objects = hstore.HStoreManager()

    class Meta:
        abstract = True


class DataBag(HStoreModel):
    name = models.CharField(max_length=32)
    data = hstore.DictionaryField()


class RefsBag(HStoreModel):
    name = models.CharField(max_length=32)
    refs = hstore.ReferencesField()


class DefaultsModel(models.Model):
    a = hstore.DictionaryField(default={})
    b = hstore.DictionaryField(default=None, null=True)
    c = hstore.DictionaryField(default={'x': '1'})


class BadDefaultsModel(models.Model):
    a = hstore.DictionaryField(default=None)


class Location(geomodels.Model):
    name = geomodels.CharField(max_length=32)
    data = hstore.DictionaryField(db_index=True)
    point = geomodels.GeometryField(db_index=True)

    objects = hstore.GeoManager()

    def __unicode__(self):
        return self.name
