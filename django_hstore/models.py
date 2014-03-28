import django

if django.get_version() < '1.7':
    from .apps import *
else:
    from django_hstore import lookups
