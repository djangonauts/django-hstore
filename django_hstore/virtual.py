from django.db import models
from django.utils import six


__all__ = [
    '_add_hstore_virtual_fields_to_fields',
    '_remove_hstore_virtual_fields_from_fields',
    'create_hstore_virtual_field',
]


def _add_hstore_virtual_fields_to_fields(self):
    """
    add hstore virtual fields to model meta fields
    """
    for field in self._meta.hstore_virtual_fields.values():
        if field not in self._meta.fields:
            self._meta.fields.append(field)

def _remove_hstore_virtual_fields_from_fields(self):
    """
    remove hstore virtual fields from model meta fields
    """
    for field in self._meta.hstore_virtual_fields.values():
        self._meta.fields.remove(field)


class HStoreVirtualMixin(object):
    """
    must be mixed-in with django fields
    """
    def contribute_to_class(self, cls, name, virtual_only=True):
        self.set_attributes_from_name(name)
        self.model = cls
        cls._meta.add_virtual_field(self)
        if self.choices:
            setattr(cls, 'get_%s_display' % self.name,
                    curry(cls._get_FIELD_display, field=self))
        
        # Connect myself as the descriptor for this field
        setattr(cls, name, self)
    
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


def create_hstore_virtual_field(field_cls, kwargs={}):
    """
    returns an instance of an HStore virtual field which is mixed with the specified field class
    and initializated with the kwargs passed
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
        def __init__(self, *args, **kwargs):
            try:
                self.hstore_field_name = kwargs.pop('hstore_field_name')
            except KeyError:
                raise ValueError('missing hstore_field_name keyword argument')
            super(VirtualField, self).__init__(*args, **kwargs)
    
    # support DateTimeField
    if BaseField == models.DateTimeField and kwargs.get('default') is None:
        import datetime
        kwargs['default'] = datetime.datetime.utcnow()
    
    field = VirtualField(**kwargs)
    
    if field.default == models.fields.NOT_PROVIDED:
        field.default = ''
    
    return field
