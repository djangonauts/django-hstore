from django.db import models, connection
from django.utils.translation import ugettext_lazy as _
from django_hstore import forms, util


class HStoreDictionary(dict):
    """
    A dictionary subclass which implements hstore support.
    """
    def __init__(self, value=None, field=None, instance=None, **params):
        super(HStoreDictionary, self).__init__(value, **params)
        self.field = field
        self.instance = instance

    def remove(self, keys):
        """
        Removes the specified keys from this dictionary.
        """
        queryset = self.instance._base_manager.get_query_set()
        queryset.filter(pk=self.instance.pk).hremove(self.field.name, keys)


class HStoreDescriptor(models.fields.subclassing.Creator):
    def __set__(self, obj, value):
        value = self.field.to_python(value)
        if isinstance(value, dict):
            value = HStoreDictionary(
                value=value, field=self.field, instance=obj
                )
        obj.__dict__[self.field.name] = value


class HStoreDict(dict):
    def __init__(self, dict):
        super(HStoreDict, self).__init__(dict)
        self.connection = None

    def prepare(self, connection):
        self.connection = connection

    def __str__(self):
        from psycopg2.extras import HstoreAdapter
        value = HstoreAdapter(self)
        if self.connection:
            value.prepare(self.connection.connection)
        return value.getquoted()


class HStoreField(models.Field):
    def __init__(self, *args, **kwargs):
        if kwargs.get('db_index', False):
            raise TypeError("'db_index' is not a valid argument for %s. Use 'python manage.py sqlhstoreindexes' instead." % self.__class__)
        super(HStoreField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        super(HStoreField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, HStoreDescriptor(self))

    def get_default(self):
        """
        Returns the default value for this field.
        """
        if self.has_default():
            if callable(self.default):
                return HStoreDict(self.default())
            return HStoreDict(self.default)
        if (
            not self.empty_strings_allowed or
                (
                self.null and
                not connection.features.interprets_empty_strings_as_nulls
                )
            ):
            return None
        return HStoreDict({})

    def get_prep_value(self, value):
        if not isinstance(value, HStoreDict):
            return HStoreDict(value)
        else:
            return value

    def get_db_prep_value(self, value, connection, prepared=False):
        if not prepared:
            value = self.get_prep_value(value)
            value.prepare(connection)
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

