import django
from django.db import models
from django.core.exceptions import ValidationError

from .fields import DictionaryField


if django.get_version() < '1.7':
    from .apps import *


class SchemaModel(models.Model):
    """
    adds support for hstore virtual fields
    """
    class Meta:
        abstract = True
    
    def clean_fields(self, exclude=None):
        """
        Cleans all fields (including hstore virtual fields) and raises a ValidationError containing a dict
        of all validation errors if any occur.
        """
        if exclude is None:
            exclude = []

        errors = {}
        for f in (self._meta.fields + self._meta.hstore_virtual_fields):
            if f.name in exclude:
                continue
            # Skip validation for empty fields with blank=True. The developer
            # is responsible for making sure they have a valid value.
            raw_value = getattr(self, f.attname)
            if f.blank and raw_value in f.empty_values:
                continue
            try:
                value = f.clean(raw_value, self)
                if not hasattr(f, 'schema'):
                    setattr(self, f.attname, value)
            except ValidationError as e:
                errors[f.name] = e.error_list

        if errors:
            raise ValidationError(errors)