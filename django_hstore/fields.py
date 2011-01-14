
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Field, SubfieldBase

class DictionaryField(Field):
    def db_type(self):
        return 'hstore'
    def get_db_prep_lookup(self, lookup, value):
        return value

class ReferencesField(Field):
    __metaclass__ = SubfieldBase
    def db_type(self):
        return 'hstore'
    def get_db_prep_lookup(self, lookup, value):
        return self.get_db_prep_value(value)

    def get_db_prep_value(self, value):
        refs = {}
        for key, instance in value.iteritems():
            refs[key] = self._identify_instance(instance)
        else:
            return refs

    def to_python(self, value):
        refs = {}
        for key, reference in value.iteritems():
            if isinstance(reference, basestring):
                refs[key] = self._acquire_reference(reference)
            else:
                refs[key] = reference
        else:
            return refs

    def _acquire_reference(self, reference):
        try:
            implementation, identifier = reference.split(':')
            module, sep, attr = implementation.rpartition('.')
            implementation = getattr(__import__(module, fromlist=(attr,)), attr)
            return implementation.objects.get(pk=identifier)
        except ObjectDoesNotExist:
            return None
        except Exception:
            raise ValueError()

    def _identify_instance(self, instance):
        implementation = type(instance)
        return '%s.%s:%s' % (implementation.__module__, implementation.__name__, instance.pk)

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules(rules=[], patterns=['django_hstore\.fields'])
except ImportError:
    pass

