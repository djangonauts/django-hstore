from django.db import models
from django.utils import six
from django.utils.functional import curry


__all__ = [
    'create_hstore_virtual_field',
    'VirtualField'
]



class HStoreVirtualMixin(object):
    """
    must be mixed-in with django fields
    """
    def contribute_to_class(self, cls, name):
        if self.choices:
            setattr(cls, 'get_%s_display' % self.name,
                    curry(cls._get_FIELD_display, field=self))
        self.attname = name
        self.name = name
        self.model = cls
        # setting column as none will tell django to not consider this a concrete field
        self.column = None
        # Connect myself as the descriptor for this field
        setattr(cls, name, self)
        # add field to class
        cls._meta.add_field(self)
        # add also into virtual fields in order to support admin
        cls._meta.virtual_fields.append(self)
    
    def db_type(self, connection):
        """
        returning None here will cause django to exclude this field
        from the concrete field list (_meta.concrete_fields)
        resulting in the fact that syncdb will skip this field when creating tables in PostgreSQL
        """
        return None
    
    # begin descriptor methods
    
    def __get__(self, instance, instance_type=None):
        """
        retrieve value from hstore dictionary
        """
        if instance is None:
            raise AttributeError('Can only be accessed via instance')
        
        return getattr(instance, self.hstore_field_name).get(self.name, self.default)
    
    def __set__(self, instance, value):
        """
        set value on hstore dictionary
        """
        hstore_dictionary = getattr(instance, self.hstore_field_name)
        hstore_dictionary[self.name] = value
    
    # end descriptor methods


# dummy class, used by django 1.7 schema editor only
class VirtualField(HStoreVirtualMixin, models.Field):
    pass


def create_hstore_virtual_field(field_cls, kwargs, hstore_field_name):
    """
    returns an instance of an HStore virtual field which is mixed-in
    with the specified field class and initializated with the kwargs passed
    """
    if isinstance(field_cls, six.string_types):
        try:
            BaseField = getattr(models, field_cls)
        except AttributeError:
            raise ValueError('specified class %s is not a standard django model field (couldn\'t find it in django.db.models)' % field_cls)
    elif issubclass(field_cls, models.Field):
        BaseField = field_cls
    else:
        raise ValueError('field must be either a django standard field or a subclass of django.db.models.Field')
        
    class VirtualField(HStoreVirtualMixin, BaseField):
        # keep basefield info (added for django-rest-framework-hstore)
        __basefield__ = BaseField
        
        def __init__(self, *args, **kwargs):
            try:
                self.hstore_field_name = hstore_field_name
            except KeyError:
                raise ValueError('missing hstore_field_name keyword argument')    
            super(VirtualField, self).__init__(*args, **kwargs)
        
        def deconstruct(self, *args, **kwargs):
            """
            specific for django 1.7 and greater (migration framework)
            """
            name, path, args, kwargs = super(VirtualField, self).deconstruct(*args, **kwargs)
            return (name, path, args, { 'default': kwargs.get('default')})
    
    # support DateTimeField
    if BaseField == models.DateTimeField and kwargs.get('default') is None:
        import datetime
        kwargs['default'] = datetime.datetime.utcnow()
    
    # support Date and DateTime in django-rest-framework-hstore
    if BaseField == models.DateTimeField or BaseField == models.DateField:
        def value_to_string(self, obj):
            val = self._get_val_from_obj(obj)
            try:
                return '' if val is None else val.isoformat()
            except AttributeError as e:
                return val
        VirtualField.value_to_string = value_to_string
    
    field = VirtualField(**kwargs)
    
    if field.default == models.fields.NOT_PROVIDED:
        field.default = ''
    
    return field


# south compatibility, ignore virtual fields
try:
    from south.modelsinspector import add_ignored_fields
    add_ignored_fields(["^django_hstore\.virtual\.VirtualField"])
except ImportError:
    pass