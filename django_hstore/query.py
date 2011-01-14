
from django.db.models.sql.where import WhereNode as BaseWhereNode
from django.db.models.sql.query import BaseQuery

def dict_to_hstore(value):
    pairs = []
    for k, v in value.iteritems():
        pairs.append('"%s"=>"%s"' % (k, v))
    else:
        return ','.join(pairs)

def hstore_to_dict(value):
    return eval('{%s}' % value.replace('=>', ':'))

class WhereNode(BaseWhereNode):
    def make_atom(self, child, qn):
        lvalue, lookup_type, value_annot, param = child
        if isinstance(lvalue, tuple) and lvalue[2] == 'hstore':
            field = self.sql_for_columns(lvalue, qn)
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
            return super(WhereNode, self).make_atom(child, qn)

class Query(BaseQuery):
    def __init__(self, model, connection):
        super(Query, self).__init__(model, connection, WhereNode)

