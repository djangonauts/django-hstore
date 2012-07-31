#-*- coding: utf-8 -*-
from django.contrib.gis.db import models
from django_hstore import hstore


class Ref(models.Model):
    name = models.CharField(max_length=32)

    def __unicode__(self):
        return self.name

class DataBag(models.Model):
    name = models.CharField(max_length=32)
    data = hstore.DictionaryField(db_index=True)

    objects = hstore.Manager()

    def __unicode__(self):
        return self.name

class RefsBag(models.Model):
    name = models.CharField(max_length=32)
    refs = hstore.ReferencesField(db_index=True)

    objects = hstore.Manager()

    def __unicode__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=32)
    data = hstore.DictionaryField(db_index=True)
    point = models.GeometryField(db_index=True)

    objects = hstore.GeoManager()

    def __unicode__(self):
        return self.name

