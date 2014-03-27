from django.db.models.fields import Field
from django.db.models.lookups import GreaterThan
from django.db.models.lookups import GreaterThanOrEqual
from django.db.models.lookups import LessThan
from django.db.models.lookups import LessThanOrEqual


class HStoreComparisonLookupMixin(object):
    """
    """

    def as_comparison_sql(self, qn , connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        if len(rhs_params) == 1 and isinstance(rhs_params[0], dict):
            param = rhs_params[0]
            sign = (self.lookup_name[0] == 'g' and '>%s' or '<%s') % (self.lookup_name[-1] == 'e' and '=' or '')
            param_keys = list(param.keys())
            return '%s->\'%s\' %s %%s' % (lhs, param_keys[0], sign), param.values()
        raise ValueError('invalid value')


class HStoreGreaterThan(HStoreComparisonLookupMixin, GreaterThan):

    def as_postgresql(self, qn, connection):
        l_db_type = self.lhs.output_type.db_type(connection=connection)
        if l_db_type == 'hstore':
            return self.as_comparison_sql(qn, connection)
        return super(HStoreGreaterThan, self).as_sql(qn, connection)


class HStoreGreaterThanOrEqual(HStoreComparisonLookupMixin, GreaterThanOrEqual):

    def as_postgresql(self, qn, connection):
        l_db_type = self.lhs.output_type.db_type(connection=connection)
        if l_db_type == 'hstore':
            return self.as_comparison_sql(qn, connection)
        return super(HStoreGreaterThanOrEqual, self).as_sql(qn, connection)


class HStoreLessThan(HStoreComparisonLookupMixin, LessThan):

    def as_postgresql(self, qn, connection):
        l_db_type = self.lhs.output_type.db_type(connection=connection)
        if l_db_type == 'hstore':
            return self.as_comparison_sql(qn, connection)
        return super(HStoreLessThan, self).as_sql(qn, connection)


class HStoreLessThanOrEqual(HStoreComparisonLookupMixin, LessThanOrEqual):

    def as_postgresql(self, qn, connection):
        l_db_type = self.lhs.output_type.db_type(connection=connection)
        if l_db_type == 'hstore':
            return self.as_comparison_sql(qn, connection)
        return super(HStoreLessThanOrEqual, self).as_sql(qn, connection)


#FIXME: what happens if another app has created a custom lookup?
Field.register_lookup(HStoreGreaterThan)
Field.register_lookup(HStoreGreaterThanOrEqual)
Field.register_lookup(HStoreLessThan)
Field.register_lookup(HStoreLessThanOrEqual)