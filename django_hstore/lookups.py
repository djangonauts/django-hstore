from __future__ import unicode_literals, absolute_import

from django.utils import six
from django.db.models.lookups import (
    GreaterThan,
    GreaterThanOrEqual,
    LessThan,
    LessThanOrEqual,
    Contains,
    IContains,
    IsNull
)

from django_hstore.utils import get_cast_for_param, get_value_annotations


__all__ = [
    'HStoreComparisonLookupMixin',
    'HStoreGreaterThan',
    'HStoreGreaterThanOrEqual',
    'HStoreLessThan',
    'HStoreLessThanOrEqual',
    'HStoreContains',
    'HStoreIContains',
    'HStoreIsNull'
]


class HStoreLookupMixin(object):
    def __init__(self, lhs, rhs, *args, **kwargs):
        # We need to record the types of the rhs parameters before they are converted to strings
        if isinstance(rhs, dict):
            self.value_annot = get_value_annotations(rhs)
        super(HStoreLookupMixin, self).__init__(lhs, rhs)


class HStoreComparisonLookupMixin(HStoreLookupMixin):
    """
    Mixin for hstore comparison custom lookups.
    """

    def as_postgresql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        if len(rhs_params) == 1 and isinstance(rhs_params[0], dict):
            param = rhs_params[0]
            sign = (self.lookup_name[0] == 'g' and '>%s' or '<%s') % (self.lookup_name[-1] == 'e' and '=' or '')
            param_keys = list(param.keys())
            conditions = []

            for key in param_keys:
                cast = get_cast_for_param(self.value_annot, key)
                conditions.append('(%s->\'%s\')%s %s %%s' % (lhs, key, cast, sign))

            return (" AND ".join(conditions), param.values())

        raise ValueError('invalid value')


class HStoreGreaterThan(HStoreComparisonLookupMixin, GreaterThan):
    pass


class HStoreGreaterThanOrEqual(HStoreComparisonLookupMixin, GreaterThanOrEqual):
    pass


class HStoreLessThan(HStoreComparisonLookupMixin, LessThan):
    pass


class HStoreLessThanOrEqual(HStoreComparisonLookupMixin, LessThanOrEqual):
    pass


class HStoreContains(HStoreLookupMixin, Contains):

    def as_postgresql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        # FIXME: ::text cast is added by ``django.db.backends.postgresql_psycopg2.DatabaseOperations.lookup_cast``;
        # maybe there's a cleaner way to fix the cast for hstore columns
        if lhs.endswith('::text'):
            lhs = '{0}{1}'.format(lhs[:-4], 'hstore')
        param = self.rhs

        if isinstance(param, dict):
            values = list(param.values())
            keys = list(param.keys())
            if len(values) == 1 and isinstance(values[0], (list, tuple)):
                # Can't cast here because the list could contain multiple types
                return '%s->\'%s\' = ANY(%%s)' % (lhs, keys[0]), [[str(x) for x in values[0]]]
            elif len(keys) == 1 and len(values) == 1:
                # Retrieve key and compare to param instead of using '@>' in order to cast hstore value
                cast = get_cast_for_param(self.value_annot, keys[0])
                return ('(%s->\'%s\')%s = %%s' % (lhs, keys[0], cast), [values[0]])
            return '%s @> %%s' % lhs, [param]
        elif isinstance(param, (list, tuple)):
            if len(param) == 0:
                raise ValueError('invalid value')
            if len(param) < 2:
                return '%s ? %%s' % lhs, [param[0]]
            if param:
                return '%s ?& %%s' % lhs, [param]
        elif isinstance(param, six.string_types):
            # if looking for a string perform the normal text lookup
            # that is: look for occurence of string in all the keys
            pass
        # needed for SerializedDictionaryField
        elif hasattr(self.lhs.target, 'serializer'):
            try:
                self.lhs.target._serialize_value(param)
                pass
            except Exception:
                raise ValueError('invalid value')
        else:
            raise ValueError('invalid value')
        return super(HStoreContains, self).as_sql(compiler, connection)


class HStoreIContains(IContains, HStoreContains):
    pass


class HStoreIsNull(IsNull):

    def as_postgresql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)

        if isinstance(self.rhs, dict):
            param = self.rhs
            param_keys = list(param.keys())
            conditions = []

            for key in param_keys:
                op = 'IS NULL' if param[key] else 'IS NOT NULL'
                conditions.append('(%s->\'%s\') %s' % (lhs, key, op))

            return (" AND ".join(conditions), lhs_params)

        return super(HStoreIsNull, self).as_sql(compiler, connection)
