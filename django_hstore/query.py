from django import VERSION
from django.db import transaction
from django.db.models.query import QuerySet
from django.db.models.sql.constants import SINGLE
from django.db.models.sql.datastructures import EmptyResultSet
from django.db.models.sql.query import Query
from django.db.models.sql.subqueries import UpdateQuery
from django.db.models.sql.where import EmptyShortCircuit, WhereNode
try:
    from django.db.models.sql.where import QueryWrapper # django <= 1.3
except ImportError:
    from django.db.models.query_utils import QueryWrapper # django >= 1.4


def select_query(method):
    def selector(self, *args, **params):
        query = self.query.clone()
        query.default_cols = False
        query.clear_select_fields()
        return method(self, query, *args, **params)
    return selector


def update_query(method):
    def updater(self, *args, **params):
        self._for_write = True
        query = method(self, self.query.clone(UpdateQuery), *args, **params)
        forced_managed = False
        if not transaction.is_managed(using=self.db):
            transaction.enter_transaction_management(using=self.db)
            forced_managed = True
        try:
            rows = query.get_compiler(self.db).execute_sql(None)
            if forced_managed:
                transaction.commit(using=self.db)
            else:
                transaction.commit_unless_managed(using=self.db)
        finally:
            if forced_managed:
                transaction.leave_transaction_management(using=self.db)
        self._result_cache = None
        return rows
    updater.alters_data = True
    return updater


class HStoreWhereNode(WhereNode):
    def make_atom(self, child, qn, connection):
        lvalue, lookup_type, value_annot, param = child
        kwargs = {'connection': connection} if VERSION[:2] >= (1, 3) else {}
        if lvalue and lvalue.field and hasattr(lvalue.field, 'db_type') and lvalue.field.db_type(**kwargs) == 'hstore':
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
                    if param:
                        return ('%s ?& %%s' % field, [param])
                    else:
                        raise ValueError('invalid value')
                elif isinstance(param, basestring):
                    return ('%s ? %%s' % field, [param])
                else:
                    raise ValueError('invalid value')
            else:
                raise TypeError('invalid lookup type')
        return super(HStoreWhereNode, self).make_atom(child, qn, connection)


class HStoreQuery(Query):
    def __init__(self, model):
        super(HStoreQuery, self).__init__(model, HStoreWhereNode)


class HStoreQuerySet(QuerySet):
    def __init__(self, model=None, query=None, using=None):
        query = query or HStoreQuery(model)
        super(HStoreQuerySet, self).__init__(model=model, query=query, using=using)

    @select_query
    def hkeys(self, query, attr):
        """
        Enumerates the keys in the specified hstore.
        """
        query.add_extra({'_': 'akeys("%s")' % attr}, None, None, None, None, None)
        result = query.get_compiler(self.db).execute_sql(SINGLE)
        return (result[0] if result else [])

    @select_query
    def hpeek(self, query, attr, key):
        """
        Peeks at a value of the specified key.
        """
        query.add_extra({'_': '%s -> %%s' % attr}, [key], None, None, None, None)
        result = query.get_compiler(self.db).execute_sql(SINGLE)
        if result and result[0]:
            field = self.model._meta.get_field_by_name(attr)[0]
            return field._value_to_python(result[0])

    @select_query
    def hslice(self, query, attr, keys):
        """
        Slices the specified key/value pairs.
        """
        query.add_extra({'_': 'slice("%s", %%s)' % attr}, [keys], None, None, None, None)
        result = query.get_compiler(self.db).execute_sql(SINGLE)
        if result and result[0]:
            field = self.model._meta.get_field_by_name(attr)[0]
            return dict((key, field._value_to_python(value)) for key, value in result[0].iteritems())
        return {}

    @update_query
    def hremove(self, query, attr, keys):
        """
        Removes the specified keys in the specified hstore.
        """
        value = QueryWrapper('delete("%s", %%s)' % attr, [keys])
        field, model, direct, m2m = self.model._meta.get_field_by_name(attr)
        query.add_update_fields([(field, None, value)])
        return query

    @update_query
    def hupdate(self, query, attr, updates):
        """
        Updates the specified hstore.
        """
        value = QueryWrapper('"%s" || %%s' % attr, [updates])
        field, model, direct, m2m = self.model._meta.get_field_by_name(attr)
        query.add_update_fields([(field, None, value)])
        return query
