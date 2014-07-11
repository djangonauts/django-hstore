from __future__ import unicode_literals, absolute_import

from django.db import models, connection
from django.utils.translation import ugettext_lazy as _
from django import get_version

from .descriptors import *
from .dict import *
from . import forms, utils


class HStoreField(models.Field):
    """ HStore Base Field """

    def validate(self, value, *args):
        super(HStoreField, self).validate(value, *args)
        forms.validate_hstore(value)

    def contribute_to_class(self, cls, name):
        super(HStoreField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, HStoreDescriptor(self))

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
        if (not self.empty_strings_allowed or (self.null and
                   not connection.features.interprets_empty_strings_as_nulls)):
            return None
        return HStoreDict({}, self)

    def get_prep_value(self, value):
        if isinstance(value, dict) and not isinstance(value, HStoreDict):
            return HStoreDict(value, self)
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

    def south_field_triple(self):
        from south.modelsinspector import introspector
        name = '%s.%s' % (self.__class__.__module__, self.__class__.__name__)
        args, kwargs = introspector(self)
        return name, args, kwargs


if get_version() >= '1.7':
    from .lookups import *

    HStoreField.register_lookup(HStoreGreaterThan)
    HStoreField.register_lookup(HStoreGreaterThanOrEqual)
    HStoreField.register_lookup(HStoreLessThan)
    HStoreField.register_lookup(HStoreLessThanOrEqual)
    HStoreField.register_lookup(HStoreContains)
    HStoreField.register_lookup(HStoreIContains)


class DictionaryField(HStoreField):
    description = _("A python dictionary in a postgresql hstore field.")

    def formfield(self, **params):
        params['form_class'] = forms.DictionaryField
        return super(DictionaryField, self).formfield(**params)

    def _value_to_python(self, value):
        return value


class ReferencesField(HStoreField):
    description = _("A python dictionary of references to model instances in an hstore field.")

    def contribute_to_class(self, cls, name):
        super(ReferencesField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, HStoreReferenceDescriptor(self))

    def formfield(self, **params):
        params['form_class'] = forms.ReferencesField
        return super(ReferencesField, self).formfield(**params)

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


# south compatibility
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules(rules=[], patterns=['django_hstore\.hstore'])
except ImportError:
    pass
