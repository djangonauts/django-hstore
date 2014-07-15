class HStoreVirtualMixin(object):
    """
    must be mixed-in with django fields
    """
    def __init__(self, *args, **kwargs):
        try:
            self.hstore_field_name = kwargs.pop('hstore_field_name')
        except KeyError:
            raise ValueError('missing hstore_field_name keyword argument')
        super(HStoreVirtualMixin, self).__init__(*args, **kwargs)
    
    def contribute_to_class(self, cls, name, virtual_only=True):
        super(HStoreVirtualMixin, self).contribute_to_class(cls, name, virtual_only)
        
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
    
    # TODO: maybe this is not necessary
    #def value_from_object(self, obj):
    #    """
    #    Returns the value of this field in the given model instance.
    #    """
    #    hstore_field = getattr(obj, self.hstore_field_name)
    #    return hstore_field[self.attname]
    
    #def save_form_data(self, instance, data):
    #    hstore_field = getattr(instance, self.hstore_field_name)
    #    hstore_field[self.attname] = data
    #    setattr(instance, self.hstore_field_name, hstore_field)