import django


if django.get_version() < '1.7':
    from .apps import *

try:
    import lookups
except:
    pass