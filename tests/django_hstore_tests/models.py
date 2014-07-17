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
    def __init__(self, *args, **kwargs):
        try:
            self.hstore_field_name = kwargs.pop('hstore_field_name')
        except KeyError:
            raise ValueError('missing hstore_field_name keyword argument')
        super(VirtualIntegerField, self).__init__(*args, **kwargs)

class VirtualFloatField(HStoreVirtualMixin, models.FloatField):
    def __init__(self, *args, **kwargs):
        try:
            self.hstore_field_name = kwargs.pop('hstore_field_name')
        except KeyError:
            raise ValueError('missing hstore_field_name keyword argument')
        super(VirtualFloatField, self).__init__(*args, **kwargs)

class VirtualCharField(HStoreVirtualMixin, models.CharField):
    def __init__(self, *args, **kwargs):
        try:
            self.hstore_field_name = kwargs.pop('hstore_field_name')
        except KeyError:
            raise ValueError('missing hstore_field_name keyword argument')
        super(VirtualCharField, self).__init__(*args, **kwargs)

class VirtualTextField(HStoreVirtualMixin, models.TextField):
    def __init__(self, *args, **kwargs):
        try:
            self.hstore_field_name = kwargs.pop('hstore_field_name')
        except KeyError:
            raise ValueError('missing hstore_field_name keyword argument')
        super(VirtualTextField, self).__init__(*args, **kwargs)


class SchemaDataBag(HStoreModel):
    name = models.CharField(max_length=32)
    data = hstore.DictionaryField(schema=['i am temporary'])

    number = VirtualIntegerField(hstore_field_name='data', default=0)
    float = VirtualFloatField(hstore_field_name='data', default=1.0)
    char = VirtualCharField(hstore_field_name='data', default='test', blank=True, max_length=10)
    text = VirtualTextField(hstore_field_name='data', blank=True)


# if geodjango is in use define Location model, which contains GIS data
if GEODJANGO:
    from django.contrib.gis.db import models as geo_models
    class Location(geo_models.Model):
        name = geo_models.CharField(max_length=32)
        data = hstore.DictionaryField()
        point = geo_models.GeometryField()
    
        objects = hstore.HStoreGeoManager()
    
    __all__.append('Location')
