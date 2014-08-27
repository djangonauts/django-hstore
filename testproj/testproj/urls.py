from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.http import HttpResponse

from .models import TestModel

import random

import uuid


def test_view(request):
    obj1 = TestModel(name=str(uuid.uuid1()), data = {"counter": 1})
    obj1.save()

    obj2 = TestModel.objects.get(pk=obj1.pk)
    obj2.data = {"foo": "bar"}
    obj2.save()
    print(type(obj1.data), type(obj2.data))
    return HttpResponse("hello world {0}, {1}".format(obj1.data, obj2.data))


urlpatterns = [
    url(r"^$", test_view)
]
