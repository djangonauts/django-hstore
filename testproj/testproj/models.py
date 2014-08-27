from django.db import models
from django_hstore import hstore


class TestModel(models.Model):
    name = models.CharField(unique=True, max_length=255)
    data = hstore.DictionaryField()
    objects = hstore.HStoreManager()
