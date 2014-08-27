print(222222222)
import django
from django.db import models
from django.core.exceptions import ValidationError

print("models.py")

from .fields import DictionaryField

if django.get_version() < '1.7':
    from . import apps
