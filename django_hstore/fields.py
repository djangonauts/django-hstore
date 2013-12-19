try:
    import simplejson as json
except ImportError:
    import json

from django.db import models, connection
from django_hstore import forms, util, exceptions
from django.utils.translation import ugettext_lazy as _


class HStoreDict(dict):
    """
    A dictionary subclass which implements hstore support.
    """
    
    def __init__(self, value=None, field=None, instance=None, connection=None, **params):
        # if passed value is string
        # ensure is json formatted
        if isinstance(value, basestring):
            try:
                value = json.loads(value)
            except ValueError as e:
                raise exceptions.HStoreDictException(
                    'HStoreDict accepts only valid json formatted strings.',
                    json_error_message=e.message
                )
        
        # allow dictionaries only
        if not isinstance(value, dict):
            raise exceptions.HStoreDictException(
                'HStoreDict accepts only dictionary objects or json formatted string representations of json objects'
            )
        
        # ensure values are acceptable
        for key, val in value.iteritems():
            value[key] = self.ensure_acceptable_value(val)
        
        super(HStoreDict, self).__init__(value, **params)
        self.field = field
        self.instance = instance
        
        # attribute that make possible
        # to use django_hstore without a custom backend
        self.connection = connection
    
    def __setitem__(self, *args, **kwargs):
        args = (args[0], self.ensure_acceptable_value(args[1]))
        super(HStoreDict, self).__setitem__(*args, **kwargs)
    
    def __str__(self):
        if self:
            return json.dumps(self)
        else:
            return ''
    
    def __unicode__(self):
        return unicode(self.__str__())
    
    def __getstate__(self):
        if self.connection:
            d = dict(self.__dict__)
            d['connection'] = None
            return d
        return self.__dict__
    
    def __copy__(self):
        return self.__class__(self, self.field, self.connection)
    
    def update(self, *args, **kwargs):
        for key, value in dict(*args, **kwargs).iteritems():
            self[key] = value
    
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
    
    def prepare(self, connection):
        self.connection = connection

    def remove(self, keys):
        """
        Removes the specified keys from this dictionary.
        """
        queryset = self.instance._base_manager.get_query_set()
        queryset.filter(pk=self.instance.pk).hremove(self.field.name, keys)


class HStoreReferenceDictionary(HStoreDict):
    """
    A dictionary which adds support to storing references to models
    """
    def __getitem__(self, *args, **kwargs):
        value = super(self.__class__, self).__getitem__(*args, **kwargs)
        # if value is a string it needs to be converted to model instance
        if isinstance(value, basestring):
            reference = util.acquire_reference(value)
            self.__setitem__(args[0], reference)
            return reference
        # otherwise just return the relation
        return value
    
    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default


class HStoreDescriptor(models.fields.subclassing.Creator):
    def __set__(self, obj, value):
        value = self.field.to_python(value)
        if isinstance(value, dict):
            value = HStoreDict(
                value=value, field=self.field, instance=obj
            )
        obj.__dict__[self.field.name] = value


class HStoreReferenceDescriptor(models.fields.subclassing.Creator):
    def __set__(self, obj, value):
        value = self.field.to_python(value)
        if isinstance(value, dict):
            value = HStoreReferenceDictionary(
                value=value, field=self.field, instance=obj
            )
        obj.__dict__[self.field.name] = value


class HStoreField(models.Field):
    """ HStore Base Field """
    
    # TODO: wtf?
    #__metaclass__ = models.SubfieldBase
    
    def __init__(self, *args, **kwargs):
        # cannot index the entire field, but internal values are indexable
        if kwargs.get('db_index', False):
            raise TypeError("'db_index' is not a valid argument for %s. Use 'python manage.py sqlhstoreindexes' instead." % self.__class__)
        
        super(HStoreField, self).__init__(*args, **kwargs)
    
    # TODO, anything changes?
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
        if (not self.empty_strings_allowed or (self.null and not connection.features.interprets_empty_strings_as_nulls)):
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
            if isinstance(value, HStoreDict):
                value.prepare(connection)
                #return value.dumps()
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
    description = _("A python dictionary of references to model instances in an hstore field.")
    
    def contribute_to_class(self, cls, name):
        super(ReferencesField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, HStoreReferenceDescriptor(self))

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
        return value if isinstance(value, dict) else HStoreReferenceDictionary({})

    def _value_to_python(self, value):
        return util.acquire_reference(value)


# south compatibility
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules(rules=[], patterns=['django_hstore\.hstore'])
except ImportError:
    pass