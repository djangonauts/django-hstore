
from django.db import models

from django_hstore import forms
from django_hstore.query import HStoreQuerySet
from django_hstore.util import serialize_references, unserialize_references

class DictionaryField(models.Field):
    """Stores a python dictionary in a postgresql hstore field."""

    __metaclass__ = models.SubfieldBase

    def db_type(self):
        return 'hstore'

    def formfield(self, **params):
        params['form_class'] = forms.DictionaryField
        return super(DictionaryField, self).formfield(**params)

    def get_prep_lookup(self, lookup, value):
        return value

    def to_python(self, value):
        return value or {}

class ReferencesField(models.Field):
    """Stores a python dictionary of references to model instances in an hstore field."""

    __metaclass__ = models.SubfieldBase

    def db_type(self):
        return 'hstore'

    def formfield(self, **params):
        params['form_class'] = forms.ReferencesField
        return super(ReferencesField, self).formfield(**params)

    def get_prep_lookup(self, lookup, value):
        return (serialize_references(value) if isinstance(value, dict) else value)

    def get_prep_value(self, value):
        return (serialize_references(value) if value else {})

    def to_python(self, value):
        return (unserialize_references(value) if value else {})

class Manager(models.Manager):
    """Object manager which enables hstore features."""

    use_for_related_fields = True

    def get_query_set(self):
        return HStoreQuerySet(self.model, using=self._db)

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules(rules=[], patterns=['django_hstore\.hstore'])
except ImportError:
    pass

