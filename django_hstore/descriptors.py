from django.db import models
from .dict import HStoreDict, HStoreReferenceDict


__all__ = [
    'HStoreDescriptor',
    'HStoreReferenceDescriptor',
    'SerializedDictDescriptor'
]


class HStoreDescriptor(models.fields.subclassing.Creator):
    _DictClass = HStoreDict

    def __init__(self, *args, **kwargs):
        self.schema_mode = kwargs.pop('schema_mode', False)
        super(HStoreDescriptor, self).__init__(*args, **kwargs)

    def __set__(self, obj, value):
        value = self.field.to_python(value)
        if isinstance(value, dict):
            value = self._DictClass(
                value=value, field=self.field, instance=obj, schema_mode=self.schema_mode
            )
        obj.__dict__[self.field.name] = value


class SerializedDictDescriptor(models.fields.subclassing.Creator):
    _DictClass = dict

    def __set__(self, obj, value):
        # Deserialization is only needed when retrieving data from DB
        # (not when field is being set via assignment (`x.data = {...}`)
        # or via the `.create()` method.
        if value and self.field._from_db(obj):
            value = self.field.to_python(value)
        obj.__dict__[self.field.name] = value


class HStoreReferenceDescriptor(HStoreDescriptor):
    _DictClass = HStoreReferenceDict
