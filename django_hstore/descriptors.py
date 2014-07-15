from django.db import models
from .dict import *


__all__ = [
    'HStoreDescriptor',
    'HStoreReferenceDescriptor'
]


class HStoreDescriptor(models.fields.subclassing.Creator):
    _DictClass = HStoreDict
    
    def __init__(self, *args, **kwargs):
        self.pickle = kwargs.pop('pickle', False)
        super(HStoreDescriptor, self).__init__(*args, **kwargs)
    
    def __set__(self, obj, value):
        value = self.field.to_python(value)
        if isinstance(value, dict):
            value = self._DictClass(
                value=value, field=self.field, instance=obj, pickle=self.pickle
            )
        obj.__dict__[self.field.name] = value


class HStoreReferenceDescriptor(HStoreDescriptor):
    _DictClass = HStoreReferenceDict