
from django.db.models import Field, SubfieldBase

from django_hstore import forms
from django_hstore import util

class DictionaryField(Field):
    """Stores a python dictionary in a postgresql hstore field."""

    def db_type(self):
        return 'hstore'

    def formfield(self, **params):
        params['form_class'] = forms.DictionaryField
        return super(DictionaryField, self).formfield(**params)

    def get_prep_lookup(self, lookup, value):
        return value

class ReferencesField(Field):
    """Stores a python dictionary of references to model instances in an hstore field."""

    __metaclass__ = SubfieldBase

    def db_type(self):
        return 'hstore'

    def formfield(self, **params):
        params['form_class'] = forms.ReferencesField
        return super(ReferencesField, self).formfield(**params)

    def get_prep_lookup(self, lookup, value):
        return self.get_prep_value(value)

    def get_prep_value(self, value):
        if isinstance(value, dict):
            return util.serialize_references(value)
        else:
            return value

    def to_python(self, value):
        return util.unserialize_references(value)

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules(rules=[], patterns=['django_hstore\.fields'])
except ImportError:
    pass

