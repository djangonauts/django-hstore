from django.db import models, connection
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import ugettext_lazy as _
from django_hstore import forms, util
from django.conf import settings
import json


class HStoreDescriptor(models.fields.subclassing.Creator):
    def __set__(self, obj, value):
        value = self.field.to_python(value)
        if isinstance(value, dict):
            value = HStoreDict(
                value=value, field=self.field
                )
        obj.__dict__[self.field.name] = value


class HStoreDict(dict):
    def __init__(self, value, field=None):
        super(HStoreDict, self).__init__(value)
        self.connection = None
        self.field = field

    def prepare(self, connection):
        self.connection = connection

    def json_dict(self):
        if self.field.default_key_type == 'json' or self.field.json_keys:
            result = {}
            for key, item in self.items():
                if self.field.default_key_type == 'json' or key in self.field.json_keys:
                    result[key] = json.dumps(item, **self.field.dump_kwargs)
        else:
            result = self
        return result

    def __str__(self):
        json_dict = self.json_dict()
        from psycopg2.extras import HstoreAdapter
        value = HstoreAdapter(json_dict)
        if self.connection:
            value.prepare(self.connection.connection)
        return value.getquoted()


class HStoreField(models.Field):
    __metaclass__ = models.SubfieldBase
    def __init__(self, *args, **kwargs):
        self.dump_kwargs = kwargs.pop('dump_kwargs', {'cls': DjangoJSONEncoder})
        self.load_kwargs = kwargs.pop('load_kwargs', {})
        self.normal_keys = kwargs.pop('normal_keys', [])
        self.json_keys = kwargs.pop('json_keys', [])
        self.default_key_type = kwargs.pop('default_key_type', 'json')

        if kwargs.get('db_index', False):
            raise TypeError("'db_index' is not a valid argument for %s. Use 'python manage.py sqlhstoreindexes' instead." % self.__class__)
        super(HStoreField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        super(HStoreField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, HStoreDescriptor(self))

    def to_python(self, value):
        if self.default_key_type == 'json' or self.json_keys:
            for key, item in value.items():
                if self.default_key_type == 'json' or key in self.json_keys:
                    if isinstance(item, str) or isinstance(item, unicode):
                        value[key] = json.loads(item, **self.load_kwargs)
                        print key
        return value

    def get_default(self):
        """
        Returns the default value for this field.
        """
        if self.has_default():
            if callable(self.default):
                return HStoreDict(self.default(), self)
            elif isinstance(self.default, dict):
                return HStoreDict(self.default, self)
            return self.default
        if (
            not self.empty_strings_allowed or
                (
                self.null and
                not connection.features.interprets_empty_strings_as_nulls
                )
            ):
            return None
        return HStoreDict({}, self)

    def get_prep_value(self, value):
        if isinstance(value, dict):
            return HStoreDict(value, self)
        else:
            return value

    def get_db_prep_value(self, value, connection, prepared=False):
        if not prepared:
            value = self.get_prep_value(value)
            if isinstance(value, HStoreDict):
                value.prepare(connection)
                return value.json_dict()
        return value

    def value_to_string(self, obj):
        return self._get_val_from_obj(obj)

    def db_type(self, connection=None):
        return 'hstore'

    def south_field_triple(self):
        from south.modelsinspector import introspector
        name = '%s.%s' % (self.__class__.__module__, self.__class__.__name__)
        args, kwargs = introspector(self)
        return name, args, kwargs


class DictionaryField(HStoreField):
    description = _("A python dictionary in a postgresql hstore field.")

    def formfield(self, **params):
        params['form_class'] = forms.DictionaryField
        return super(DictionaryField, self).formfield(**params)

    def _value_to_python(self, value):
        return value


class ReferencesField(HStoreField):
    description = _(
        "A python dictionary of references to model instances in an hstore "
        "field."
        )

    def formfield(self, **params):
        params['form_class'] = forms.ReferencesField
        return super(ReferencesField, self).formfield(**params)

    def get_prep_lookup(self, lookup, value):
        if isinstance(value, dict):
            return util.serialize_references(value)
        return value

    def get_prep_value(self, value):
        return util.serialize_references(value)

    def to_python(self, value):
        return util.unserialize_references(value)

    def _value_to_python(self, value):
        return util.acquire_reference(value)

if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
    try:
        from jsonfield.fields import JSONField
        DictionaryField = JSONField
    except ImportError:
        pass
