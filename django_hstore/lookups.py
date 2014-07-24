from __future__ import unicode_literals, absolute_import

from django.utils import six
from django.db.models.lookups import (
    GreaterThan,
    GreaterThanOrEqual,
    LessThan,
    LessThanOrEqual,
    Contains,
    IContains
)


__all__ = [
    'HStoreComparisonLookupMixin',
    'HStoreGreaterThan',
    'HStoreGreaterThanOrEqual',
    'HStoreLessThan',
    'HStoreLessThanOrEqual',
    'HStoreContains',
    'HStoreIContains'
]


class HStoreComparisonLookupMixin(object):
    """
    Mixin for hstore comparison custom lookups.
    """

    def as_postgresql(self, qn , connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        if len(rhs_params) == 1 and isinstance(rhs_params[0], dict):
            param = rhs_params[0]
            sign = (self.lookup_name[0] == 'g' and '>%s' or '<%s') % (self.lookup_name[-1] == 'e' and '=' or '')
            param_keys = list(param.keys())
            conditions = []

            for key in param_keys:
                conditions.append('(%s->\'%s\') %s %%s' % (lhs, key, sign))

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


class HStoreContains(Contains):

    def as_postgresql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)

        # FIXME: ::text cast is added by ``django.db.backends.postgresql_psycopg2.DatabaseOperations.lookup_cast``;
        # maybe there's a cleaner way to fix the cast for hstore columns
        if lhs.endswith('::text'):
            lhs = lhs[:-4] + 'hstore'

        param = self.rhs

        if isinstance(param, dict):
            values = list(param.values())
            keys = list(param.keys())

            if len(values) == 1 and isinstance(values[0], (list, tuple)):
                return '%s->\'%s\' = ANY(%%s)' % (lhs, keys[0]), [[str(x) for x in values[0]]]

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
        else:
            raise ValueError('invalid value')
        return super(HStoreContains, self).as_sql(qn, connection)


class HStoreIContains(IContains, HStoreContains):
    pass
