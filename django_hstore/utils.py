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


def register_hstore(conn_or_curs, globally=False, _unicode=False, oid=None, array_oid=None):
    from psycopg2.extras import HstoreAdapter
    from psycopg2 import extensions as _ext
    import psycopg2
    import sys
    import re as regex
    from .fields import HStoreDict

    def cast(s, cur, _bsdec=regex.compile(r"\\(.)")):
        if sys.version_info[0] < 3 and _unicode:
            result = HstoreAdapter.parse_unicode(s, cur)
        else:
            result = HstoreAdapter.parse(s, cur, _bsdec)
        return HStoreDict(result)

    if oid is None:
        oid = HstoreAdapter.get_oids(conn_or_curs)
        if oid is None or not oid[0]:
            raise psycopg2.ProgrammingError(
                "hstore type not found in the database. "
                "please install it from your 'contrib/hstore.sql' file")
        else:
            array_oid = oid[1]
            oid = oid[0]

    if isinstance(oid, int):
        oid = (oid,)

    if array_oid is not None:
        if isinstance(array_oid, int):
            array_oid = (array_oid,)
        else:
            array_oid = tuple([x for x in array_oid if x])

    HSTORE = _ext.new_type(oid, str("HSTORE"), cast)
    _ext.register_type(HSTORE, not globally and conn_or_curs or None)
    _ext.register_adapter(dict, HstoreAdapter)

    if array_oid:
        HSTOREARRAY = _ext.new_array_type(array_oid, str("HSTOREARRAY"), HSTORE)
        _ext.register_type(HSTOREARRAY, not globally and conn_or_curs or None)
