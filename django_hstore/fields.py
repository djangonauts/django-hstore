from __future__ import unicode_literals, absolute_import
import json
import datetime
from pkg_resources import parse_version

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import six
from django import get_version

from .descriptors import HStoreDescriptor, HStoreReferenceDescriptor, SerializedDictDescriptor
from .dict import HStoreDict, HStoreReferenceDict
from .virtual import create_hstore_virtual_field
from . import forms, utils


class HStoreField(models.Field):
    """ HStore Base Field """

    def __init_dict(self, value):
        """
        initializes HStoreDict
        """
        return HStoreDict(value, self)

    def validate(self, value, *args):
        super(HStoreField, self).validate(value, *args)
        forms.validate_hstore(value, is_serialized=hasattr(self, 'serializer'))

    def contribute_to_class(self, cls, name):
        super(HStoreField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, HStoreDescriptor(self))

    def get_default(self):
        """
        Returns the default value for this field.
        """
        # if default defined
        if self.has_default():
            # if default is callable
            if callable(self.default):
                return self.__init_dict(self.default())
            # if it's a dict
            elif isinstance(self.default, dict):
                return self.__init_dict(self.default)
            # else just return it
            return self.default
        # default to empty dict
        return self.__init_dict({})

    def get_prep_value(self, value):
        if isinstance(value, dict) and not isinstance(value, HStoreDict):
            return self.__init_dict(value)
        else:
            return value

    def get_db_prep_value(self, value, connection, prepared=False):
        if not prepared:
            value = self.get_prep_value(value)
        return value

    def value_to_string(self, obj):
        return self._get_val_from_obj(obj)

    def db_type(self, connection=None):
        return 'hstore'

    def south_field_triple(self):  # pragma no cover
        from south.modelsinspector import introspector
        name = '%s.%s' % (self.__class__.__module__, self.__class__.__name__)
        args, kwargs = introspector(self)
        return name, args, kwargs


if parse_version(get_version()) >= parse_version('1.7'):
    from .lookups import (HStoreGreaterThan, HStoreGreaterThanOrEqual, HStoreLessThan,
                          HStoreLessThanOrEqual, HStoreContains, HStoreIContains, HStoreIsNull)

    HStoreField.register_lookup(HStoreGreaterThan)
    HStoreField.register_lookup(HStoreGreaterThanOrEqual)
    HStoreField.register_lookup(HStoreLessThan)
    HStoreField.register_lookup(HStoreLessThanOrEqual)
    HStoreField.register_lookup(HStoreContains)
    HStoreField.register_lookup(HStoreIContains)
    HStoreField.register_lookup(HStoreIsNull)


class DictionaryField(HStoreField):
    description = _("A python dictionary in a postgresql hstore field.")

    def __init__(self, *args, **kwargs):
        self.schema = kwargs.pop('schema', None)
        self.schema_mode = False
        # if schema parameter is supplied the behaviour is slightly different
        if self.schema is not None:
            self._validate_schema(self.schema)
            self.schema_mode = True
            # DictionaryField with schema is not editable via admin
            kwargs['editable'] = False
            # null defaults to True to facilitate migrations
            kwargs['null'] = kwargs.get('null', True)

        super(DictionaryField, self).__init__(*args, **kwargs)

    def __init_dict(self, value):
        """
        init HStoreDict
        pass schema_mode=True if in "schema" mode
        """
        return HStoreDict(value, self, schema_mode=self.schema_mode)

    def contribute_to_class(self, cls, name):
        super(DictionaryField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, HStoreDescriptor(self, schema_mode=self.schema_mode))

        if self.schema:
            self._create_hstore_virtual_fields(cls, name)

    def formfield(self, **kwargs):
        kwargs['form_class'] = forms.DictionaryField
        return super(DictionaryField, self).formfield(**kwargs)

    def _value_to_python(self, value):
        return value

    def south_field_triple(self):  # pragma no cover
        name, args, kwargs = super(DictionaryField, self).south_field_triple()
        # if schema mode replace the default value {} with None as {} would break south
        if self.schema_mode:
            kwargs['default'] = None
        return name, args, kwargs

    def _validate_schema(self, schema):
        if not isinstance(schema, list):
            raise ValueError('schema parameter must be a list')

        if len(schema) == 0:
            raise ValueError('schema parameter cannot be an empty list')

        for field in schema:
            if not isinstance(field, dict):
                raise ValueError('schema parameter must contain dicts representing fields, read the docs to see the format')
            if 'name' not in field:
                raise ValueError('schema element %s is missing the name key' % field)
            if 'class' not in field:
                raise ValueError('schema element %s is missing the class key' % field)

    def _create_hstore_virtual_fields(self, cls, hstore_field_name):
        """
        this methods creates all the virtual fields automatically by reading the schema attribute
        """
        if not self.schema and self.schema_mode is False:
            return
        # add hstore_virtual_fields attribute to class
        if not hasattr(cls, '_hstore_virtual_fields'):
            cls._hstore_virtual_fields = {}
        # loop over all fields defined in schema
        for field in self.schema:
            # initialize the virtual field by specifying the class, the kwargs and the hstore field name
            virtual_field = create_hstore_virtual_field(field['class'],
                                                        field.get('kwargs', {}),
                                                        hstore_field_name)
            # this will call the contribute_to_class method in virtual.HStoreVirtualMixin
            cls.add_to_class(field['name'], virtual_field)
            # add this field to hstore_virtual_fields dict
            cls._hstore_virtual_fields[field['name']] = virtual_field

    def reload_schema(self, schema):
        """
        Reload schema arbitrarily at run-time
        """
        if schema:
            self._validate_schema(schema)
            self.schema = schema
            self.schema_mode = True
            self.editable = False
        else:
            self.schema = None
            self.schema_mode = False
            self.editable = True
        # remove any existing virtual field
        self._remove_hstore_virtual_fields()
        # set new descriptor on model class
        setattr(self.model, self.name, HStoreDescriptor(self, schema_mode=self.schema_mode))
        # create virtual fields
        self._create_hstore_virtual_fields(self.model, self.name)

    def _remove_hstore_virtual_fields(self):
        """ remove hstore virtual fields from class """
        cls = self.model
        # remove all hstore virtual fields related attributes
        if hasattr(cls, '_hstore_virtual_fields'):
            # remove attributes from class
            for field_name in cls._hstore_virtual_fields.keys():
                delattr(cls, field_name)
            delattr(cls, '_hstore_virtual_fields')
        # django >= 1.8
        if parse_version(get_version()[0:3]) >= parse_version('1.8'):
            # remove  all hstore virtual fields from meta
            hstore_fields = []
            # get all the existing hstore virtual fields
            for field in getattr(cls._meta, 'virtual_fields'):
                if hasattr(field, 'hstore_field_name'):
                    hstore_fields.append(field)
            # remove from meta
            for field in hstore_fields:
                getattr(cls._meta, 'virtual_fields').remove(field)
            # reset _meta.fields
            fields = [f for f in cls._meta.fields if not hasattr(f, 'hstore_field_name')]
            # cls._meta.fields.__class__ == ImmutableList
            cls._meta.fields = cls._meta.fields.__class__(fields)
        # django <= 1.7
        # TODO: will removed when django 1.7 will be deprecated
        else:
            # remove  all hstore virtual fields from meta
            for meta_fields in ['fields', 'local_fields', 'virtual_fields']:
                hstore_fields = []
                # get all the existing hstore virtual fields
                for field in getattr(cls._meta, meta_fields):
                    if hasattr(field, 'hstore_field_name'):
                        hstore_fields.append(field)
                # remove from meta
                for field in hstore_fields:
                    getattr(cls._meta, meta_fields).remove(field)


class ReferencesField(HStoreField):
    description = _("A python dictionary of references to model instances in an hstore field.")

    def contribute_to_class(self, cls, name):
        super(ReferencesField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, HStoreReferenceDescriptor(self))

    def formfield(self, **kwargs):
        kwargs['form_class'] = forms.ReferencesField
        return super(ReferencesField, self).formfield(**kwargs)

    def get_prep_lookup(self, lookup, value):
        if isinstance(value, dict):
            return utils.serialize_references(value)
        return value

    def get_prep_value(self, value):
        return utils.serialize_references(value)

    def to_python(self, value):
        return value if isinstance(value, dict) else HStoreReferenceDict({})

    def _value_to_python(self, value):
        return utils.acquire_reference(value)


class SerializedDictionaryField(HStoreField):
    description = _("A python dictionary in a postgresql hstore field.")

    def __init__(self, serializer=json.dumps, deserializer=json.loads, *args, **kwargs):
        self.serializer = serializer
        self.deserializer = deserializer
        super(SerializedDictionaryField, self).__init__(*args, **kwargs)

    def _from_db(self, model_instance):
        """
        Helper to determine if model instance is from the DB.
        """
        return bool(model_instance._state.adding and model_instance.pk)

    def get_default(self):
        """
        Returns the default value for this field.
        """
        if self.has_default():
            if callable(self.default):
                return self.default()
            return self.default
        else:
            return {}

    def clean(self, value, model_instance):
        if self._from_db(model_instance):  # Only prepare data from DB
            value = self.to_python(value)
        self.validate(value, model_instance)
        self.run_validators(value)
        return value

    def _serialize_value(self, value):
        # Don't serialize None type or Datetime, Postgres can handle
        if (value is None) or isinstance(value, datetime.date):
            return value
        else:
            return self.serializer(value)

    def _serialize_dict(self, value):
        if value is None:
            return value
        return dict((k, self._serialize_value(v)) for k, v in value.items())

    def _deserialize_value(self, value):
        if value is None or isinstance(value, datetime.date):
            return value
        # needed for #111
        elif not isinstance(value, six.string_types):
            return value
        else:
            return self.deserializer(value)

    def _deserialize_dict(self, value):
        """ Helper to deserialize dict-like data """
        if not value or isinstance(value, six.string_types):
            return value
        return dict((k, self._deserialize_value(v)) for k, v in value.items())

    def contribute_to_class(self, cls, name):
        super(SerializedDictionaryField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, SerializedDictDescriptor(self))

    def formfield(self, **kwargs):
        kwargs['form_class'] = forms.SerializedDictionaryField
        return super(SerializedDictionaryField, self).formfield(**kwargs)

    def get_prep_value(self, value):
        """ Convert to query-friendly format. """
        if not isinstance(value, dict):  # Handle values from hremove
            return value
        return self._serialize_dict(value)

    def get_prep_lookup(self, lookup_type, value):
        """ Prepares value for the database prior to be used in a lookup """
        if lookup_type == 'isnull':
            return value
        return self.get_prep_value(value)

    def _value_to_python(self, value):
        return self._deserialize_value(value)

    def to_python(self, value):
        """ Convert from db-friendly format to originally typed values. """
        if isinstance(value, dict):
            return self._deserialize_dict(value)
        else:
            return value


# south compatibility
try:  # pragma no cover
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules(rules=[], patterns=['django_hstore\.hstore'])
except ImportError:
    pass
