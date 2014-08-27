from __future__ import unicode_literals, absolute_import

from django.core.exceptions import ObjectDoesNotExist
from django.utils import six


def acquire_reference(reference):
    try:
        implementation, identifier = reference.split(':')
        module, sep, attr = implementation.rpartition('.')
        implementation = getattr(__import__(module, fromlist=(attr,)), attr)
        return implementation.objects.get(pk=identifier)
    except ObjectDoesNotExist:
        return None
    except Exception:
        raise ValueError


def identify_instance(instance):
    implementation = type(instance)
    return '%s.%s:%s' % (implementation.__module__, implementation.__name__, instance.pk)


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
