from django.db import models
from django.utils import six
from django.utils.functional import curry


__all__ = ['create_hstore_virtual_field']



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
        def __init__(self, *args, **kwargs):
            try:
                self.hstore_field_name = hstore_field_name
            except KeyError:
                raise ValueError('missing hstore_field_name keyword argument')
            super(VirtualField, self).__init__(*args, **kwargs)
        
        def deconstruct(self, *args, **kwargs):
            """
            substitute path with the path of the BaseField
            in order to avoid breaking the django 1.7 migration framework
            
            if this pull request gets accepted this method can be removed:
                https://code.djangoproject.com/ticket/23159
                https://github.com/django/django/pull/3013
            """
            name, path, args, kwargs = super(VirtualField, self).deconstruct(*args, **kwargs)
            # Work out path - we shorten it for known Django core fields
            path = "%s.%s" % (BaseField.__module__, BaseField.__name__)
            if path.startswith("django.db.models.fields.related"):
                path = path.replace("django.db.models.fields.related", "django.db.models")
            if path.startswith("django.db.models.fields.files"):
                path = path.replace("django.db.models.fields.files", "django.db.models")
            if path.startswith("django.db.models.fields.proxy"):
                path = path.replace("django.db.models.fields.proxy", "django.db.models")
            if path.startswith("django.db.models.fields"):
                path = path.replace("django.db.models.fields", "django.db.models")
            return (
                name,
                path,
                args,
                kwargs
            )
    
    # support DateTimeField
    if BaseField == models.DateTimeField and kwargs.get('default') is None:
        import datetime
        kwargs['default'] = datetime.datetime.utcnow()
    
    field = VirtualField(**kwargs)
    
    if field.default == models.fields.NOT_PROVIDED:
        field.default = ''
    
    return field
