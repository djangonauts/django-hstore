from __future__ import unicode_literals, absolute_import

from decimal import Decimal
from datetime import date, time, datetime

from django.core.exceptions import ObjectDoesNotExist
from django.utils import six


def acquire_reference(reference):
    try:
        model, identifier = reference.split(':')
        module, sep, attr = model.rpartition('.')
        model = getattr(__import__(module, fromlist=(attr,)), attr)
        return model.objects.get(pk=identifier)
    except ObjectDoesNotExist:
        return None
    except Exception:
        raise ValueError


def identify_instance(instance):
    model = type(instance)
    return '%s.%s:%s' % (model.__module__, model.__name__, instance.pk)


def serialize_references(references):
    refs = {}
    # if None or string return empty dict
    if references is None or isinstance(references, six.string_types):
        return {}
    # if dictionary do serialization
    elif isinstance(references, dict):
        for key, instance in references.items():
            if not isinstance(instance, six.string_types):
                refs[key] = identify_instance(instance)
            else:
                refs[key] = instance
        else:
            return refs
    # else just return the object, might be doing some other operation and we don't want to interfere
    else:
        return references


def unserialize_references(references):
    refs = {}
    if references is None:
        return refs
    for key, reference in references.items():
        if isinstance(reference, six.string_types):
            refs[key] = acquire_reference(reference)
        else:
            refs[key] = reference
    else:
        return refs


def get_cast_for_param(value_annot, key):
    if not isinstance(value_annot, dict):
        return ''
    if value_annot[key] in (True, False):
        return '::boolean'
    elif issubclass(value_annot[key], datetime):
        return '::timestamp'
    elif issubclass(value_annot[key], date):
        return '::date'
    elif issubclass(value_annot[key], time):
        return '::time'
    elif issubclass(value_annot[key], six.integer_types):
        return '::bigint'
    elif issubclass(value_annot[key], float):
        return '::float8'
    elif issubclass(value_annot[key], Decimal):
        return '::numeric'
    else:
        return ''


def get_value_annotations(param):
    # We need to store the actual value for booleans, not just the type, for isnull
    get_type = lambda v: v if isinstance(v, bool) else type(v)
    return dict((key, get_type(subvalue)) for key, subvalue in six.iteritems(param))
