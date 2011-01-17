
from django.db.models.manager import Manager
from django.db.models.query import QuerySet
from django.db.models.sql.datastructures import EmptyResultSet
from django.db.models.sql.query import Query
from django.db.models.sql.where import EmptyShortCircuit, WhereNode

from django_hstore.util import dict_to_hstore

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
                    return ('%s = %%s' % field, [dict_to_hstore(param)])
                else:
                    raise ValueError('invalid value')
            elif lookup_type == 'contains':
                if isinstance(param, dict):
                    return ('%s @> %%s' % field, [dict_to_hstore(param)])
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
        query = query or HStoreQuery(model)
        super(HStoreQuerySet, self).__init__(model=model, query=query, using=using)

class HStoreManager(Manager):
    """Object manager which enables hstore features."""

    use_for_related_fields = True

    def get_query_set(self):
        return HStoreQuerySet(self.model, using=self._db)

