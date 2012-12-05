from django.db import models
from django_hstore import hstore


class Ref(models.Model):
    name = models.CharField(max_length=32)


class HStoreModel(models.Model):
    objects = hstore.HStoreManager()

    class Meta:
        abstract = True


class DataBag(HStoreModel):
    name = models.CharField(max_length=32)
    data = hstore.DictionaryField(json_keys=['json'], default_key_type='normal')

class JsonBag(HStoreModel):
    name = models.CharField(max_length=32)
    data = hstore.DictionaryField(normal_keys=['normal'])

class RefsBag(HStoreModel):
    name = models.CharField(max_length=32)
    refs = hstore.ReferencesField()


class DefaultsModel(models.Model):
    a = hstore.DictionaryField(default={}, default_key_type='normal')
    b = hstore.DictionaryField(default=None, null=True, default_key_type='normal')
    c = hstore.DictionaryField(default={'x': '1'}, default_key_type='normal')


class BadDefaultsModel(models.Model):
    a = hstore.DictionaryField(default=None, default_key_type='normal')

