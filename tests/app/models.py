
from django.db import models
from django_hstore import hstore

class Ref(models.Model):
    name = models.CharField(max_length=32)

    def __unicode__(self):
        return self.name

class Bag(models.Model):
    name = models.CharField(max_length=32)
    data = hstore.DictionaryField()
    refs = hstore.ReferencesField()
    objects = hstore.Manager()

    def __unicode__(self):
        return self.name

