import django
from .fields import DictionaryField  # noqa


if django.get_version() < '1.7':
    from . import apps  # noqa
