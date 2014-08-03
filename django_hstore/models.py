import django
from django.db import models
from django.core.exceptions import ValidationError

from .fields import DictionaryField


if django.get_version() < '1.7':
    from . import apps
