from django.db import models
from django.conf import settings

from django_hstore import hstore

# determine if geodjango is in use
GEODJANGO = settings.DATABASES['default']['ENGINE'] == 'django.contrib.gis.db.backends.postgis'


__all__ = [
    'Ref',
    'DataBag',
    'NullableDataBag',
    'RefsBag',
    'NullableRefsBag',
    'DefaultsModel',
    'BadDefaultsModel',
    'DefaultsInline',
    'NumberedDataBag',
    'UniqueTogetherDataBag',
    'SchemaDataBag',
    'GEODJANGO'
]


class Ref(models.Model):
    name = models.CharField(max_length=32)


class HStoreModel(models.Model):
    objects = hstore.HStoreManager()

    class Meta:
        abstract = True


class DataBag(HStoreModel):
    name = models.CharField(max_length=32)
    data = hstore.DictionaryField()


class NullableDataBag(HStoreModel):
    name = models.CharField(max_length=32)
    data = hstore.DictionaryField(null=True)

class RefsBag(HStoreModel):
    name = models.CharField(max_length=32)
    refs = hstore.ReferencesField()


class NullableRefsBag(HStoreModel):
    name = models.CharField(max_length=32)
    refs = hstore.ReferencesField(null=True, blank=True)


class DefaultsModel(models.Model):
    a = hstore.DictionaryField(default={})
    b = hstore.DictionaryField(default=None, null=True)
    c = hstore.DictionaryField(default={'x': '1'})


class BadDefaultsModel(models.Model):
    a = hstore.DictionaryField(default=None)


class DefaultsInline(models.Model):
    parent = models.ForeignKey(DefaultsModel)
    d = hstore.DictionaryField(default={ 'default': 'yes' })


class NumberedDataBag(HStoreModel):
    name = models.CharField(max_length=32)
    data = hstore.DictionaryField()
    number = models.IntegerField()


class UniqueTogetherDataBag(HStoreModel):
    name = models.CharField(max_length=32)
    data = hstore.DictionaryField()
    
    class Meta:
        unique_together =  ("name", "data")


from django_hstore.virtual import HStoreVirtualMixin
from django.db import models

class VirtualIntegerField(HStoreVirtualMixin, models.IntegerField):
    pass

class SchemaDataBag(HStoreModel):
    name = models.CharField(max_length=32)
    data = hstore.DictionaryField(schema=['i am temporary'])
    # the ModeledDictionaryField should create the virtual fields automatically
    # each created virtualfield should be initialized with an on the fly created (metaprogramming)
    # virtual field which should be the result of for example IntegerField and VirtualFieldMixin
    # validation should be handled by the VirtualField only, no HStoreModelValidation shit
    number = VirtualIntegerField(hstore_field_name='data', default=0)


# if geodjango is in use define Location model, which contains GIS data
if GEODJANGO:
    from django.contrib.gis.db import models as geo_models
    class Location(geo_models.Model):
        name = geo_models.CharField(max_length=32)
        data = hstore.DictionaryField()
        point = geo_models.GeometryField()
    
        objects = hstore.HStoreGeoManager()
    
    __all__.append('Location')
