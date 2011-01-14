
from django.db.models import Field, SubfieldBase

from django_hstore.query import dict_to_hstore, hstore_to_dict

class DictionaryField(Field):
    __metaclass__ = SubfieldBase
    def db_type(self):
        return 'hstore'
    def get_db_prep_lookup(self, lookup, value):
        return value
    def get_db_prep_value(self, value):
        return dict_to_hstore(value)
    def to_python(self, value):
        if isinstance(value, basestring):
            return hstore_to_dict(value)
        else:
            return value

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules(rules=[], patterns=['fanforce\.django_hstore\.fields'])
except ImportError:
    pass

