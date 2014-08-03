from django.db import models
from django.conf import settings
from django import get_version

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

if get_version()[0:3] >= '1.6':
    class SchemaDataBag(HStoreModel):
        name = models.CharField(max_length=32)
        data = hstore.DictionaryField(schema=[
            {
                'name': 'number',
                'class': 'IntegerField',
                'kwargs': {
                    'default': 0
                }
            },
            {
                'name': 'float',
                'class': models.FloatField,
                'kwargs': {
                    'default': 1.0
                }
            },
            {
                'name': 'boolean',
                'class': 'BooleanField',
            },
            {
                'name': 'boolean_true',
                'class': 'BooleanField',
                'kwargs': {
                    'verbose_name': 'boolean true',
                    'default': True
                }
            },
            {
                'name': 'char',
                'class': 'CharField',
                'kwargs': {
                    'default': 'test', 'blank': True, 'max_length': 10
                }
            },
            {
                'name': 'text',
                'class': 'TextField',
                'kwargs': {
                    'blank': True
                }
            },
            {
                'name': 'choice',
                'class': 'CharField',
                'kwargs': {
                    'blank': True,
                    'max_length': 10,
                    'choices': (('choice1', 'choice1'), ('choice2', 'choice2')),
                    'default': 'choice1'
                }
            },
            {
                'name': 'choice2',
                'class': 'CharField',
                'kwargs': {
                    'blank': True,
                    'max_length': 10,
                    'choices': (('choice1', 'choice1'), ('choice2', 'choice2')),
                }
            },
            {
                'name': 'date',
                'class': 'DateField',
                'kwargs': {
                    'blank': True
                }
            },
            {
                'name': 'datetime',
                'class': 'DateTimeField',
                'kwargs': {
                    'blank': True
                }
            },
            {
                'name': 'decimal',
                'class': 'DecimalField',
                'kwargs': {
                    'blank': True,
                    'decimal_places': 2,
                    'max_digits': 4
                }
            },
            {
                'name': 'email',
                'class': 'EmailField',
                'kwargs': {
                    'blank': True
                }
            },
            {
                'name': 'ip',
                'class': 'GenericIPAddressField',
                'kwargs': {
                    'blank': True,
                    'null': True
                }
            },
            {
                'name': 'url',
                'class': models.URLField,
                'kwargs': {
                    'blank': True
                }
            },
        ])
    
    __all__.append('SchemaDataBag')


# if geodjango is in use define Location model, which contains GIS data
if GEODJANGO:
    from django.contrib.gis.db import models as geo_models
    class Location(geo_models.Model):
        name = geo_models.CharField(max_length=32)
        data = hstore.DictionaryField()
        point = geo_models.GeometryField()
    
        objects = hstore.HStoreGeoManager()
    
    __all__.append('Location')
