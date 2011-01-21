
from django.db.models.manager import Manager
from django.db.models.query import QuerySet
from django.db.models.sql.constants import SINGLE
from django.db.models.sql.datastructures import EmptyResultSet
from django.db.models.sql.query import Query
from django.db.models.sql.where import EmptyShortCircuit, WhereNode

class HStoreWhereNode(WhereNode):
    def make_atom(self, child, qn, connection):
        lvalue, lookup_type, value_annot, param = child
        if lvalue.field.db_type() == 'hstore':
            try:
                lvalue, params = lvalue.process(lookup_type, param, connection)
            except EmptyShortCircuit:
                raise EmptyResultSet
            field = self.sql_for_columns(lvalue, qn, connection)
            if lookup_type == 'exact':
                if isinstance(param, dict):
                    return ('%s = %%s' % field, [param])
                else:
                    raise ValueError('invalid value')
            elif lookup_type == 'contains':
                if isinstance(param, dict):
                    return ('%s @> %%s' % field, [param])
                elif isinstance(param, (list, tuple)):
                    return ('%s ?& ARRAY[%s]' % (field, ','.join(['%s'] * len(param))), param)
                elif isinstance(param, basestring):
                    return ('%s ? %%s' % field, [param])
                else:
                    raise ValueError('invalid value')
            else:
                raise TypeError('invalid lookup type')
        else:
            return super(HStoreWhereNode, self).make_atom(child, qn, connection)

class HStoreQuery(Query):
    def __init__(self, model):
        super(HStoreQuery, self).__init__(model, HStoreWhereNode)

class HStoreQuerySet(QuerySet):
    def __init__(self, model=None, query=None, using=None):
        super(HStoreQuerySet, self).__init__(model=model, query=(query or HStoreQuery(model)), using=using)

    def peek(self, attr, key):
        query = self.query.clone()
        query.add_extra({'_': "%s -> %%s" % attr}, [key], None, None, None, None)
        query.default_cols = False
        query.clear_select_fields()
        result = query.get_compiler(self.db).execute_sql(SINGLE)
        return (result[0] if result else None)

    def pull(self, attr, keys):
        """Pulls the specified keys from the specified hstore attribute."""

        query = self.query.clone()
        clause = 'slice(%s, ARRAY[%s])' % (attr, ','.join("'%s'" % key for key in keys))
        query.add_extra({'_v': clause}, None, None, None, None, None)
        query.default_cols = False
        query.clear_select_fields()
        result = query.get_compiler(self.db).execute_sql(SINGLE)
        return (result[0] if result else None)

