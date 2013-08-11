try:
    import simplejson as json
except ImportError:
    import json

from django.db import models, connection
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from django_hstore import forms, util, exceptions


class HStoreDictionary(dict):
    """
    A dictionary subclass which implements hstore support.
    """
    def __init__(self, value=None, field=None, instance=None, **params):
        if isinstance(value, basestring):
            try:
                value = json.loads(value)
            except json.scanner.JSONDecodeError as e:
                raise exceptions.HStoreDictionaryException(
                    _('HStoreDictionary accepts only dictionaries or valid json formatted strings.\n%s') % e.message,
                    json_error_message = e.message
                )
        
        # ensure values are acceptable
        for key,val in value.iteritems():
            value[key] = self.ensure_acceptable_value(val)
        
        super(HStoreDictionary, self).__init__(value, **params)
        self.field = field
        self.instance = instance
    
    def ensure_acceptable_value(self, value):
        """
        - ensure booleans, integers, floats, lists and dicts are converted to string
        - convert True and False objects to "true" and "false" so they can be
          decoded back with the json library if needed
        - convert lists and dictionaries to json formatted strings
        - leave alone all other objects because they might be representation of django models
        """
        if isinstance(value, bool):
            return unicode(value).lower()
        elif isinstance(value, int) or isinstance(value, float):
            return unicode(value)
        elif isinstance(value, list) or isinstance(value, dict):
            return json.dumps(value)
        else:
            return value
    
    def __setitem__(self, *args, **kwargs):
        args = (args[0], self.ensure_acceptable_value(args[1]))
        super(self.__class__, self).__setitem__(*args, **kwargs)

    def remove(self, keys):
        """
        Removes the specified keys from this dictionary.
        """
        queryset = self.instance._base_manager.get_query_set()
        queryset.filter(pk=self.instance.pk).hremove(self.field.name, keys)

    def __str__(self):
        if self:
            return json.dumps(self)
        else:
            return ''

    def __unicode__(self):
        if self:
            return json.dumps(self)
        else:
            return ''


class HStoreDescriptor(models.fields.subclassing.Creator):
    def __set__(self, obj, value):
        value = self.field.to_python(value)
        if isinstance(value, dict):
            value = HStoreDictionary(
                value=value, field=self.field, instance=obj
            )
        obj.__dict__[self.field.name] = value


class HStoreField(models.Field):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('db_index', True)
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
                return self.default()
            return self.default
        if (not self.empty_strings_allowed or (self.null and not connection.features.interprets_empty_strings_as_nulls)):
            return None
        return {}

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
    description = _("A python dictionary of references to model instances in an hstore field.")

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


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules(rules=[], patterns=['django_hstore\.hstore'])
except ImportError:
    pass