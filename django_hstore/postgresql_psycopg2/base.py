from psycopg2.extras import register_hstore

from django import VERSION
from django.db.backends.postgresql_psycopg2.base import *
from django.db.backends.util import truncate_name

class DatabaseCreation(DatabaseCreation):
    def sql_indexes_for_field(self, model, f, style):
        kwargs = VERSION[:2] >= (1, 3) and {'connection': self.connection} or {}
        if f.db_type(**kwargs) == 'hstore':
            if not f.db_index:
                return []
            qn = self.connection.ops.quote_name
            tablespace = f.db_tablespace or model._meta.db_tablespace
            tablespace_sql = ''
            if tablespace:
                sql = self.connection.ops.tablespace_sql(tablespace)
                if sql:
                    tablespace_sql = ' ' + sql
            index_name = '%s_%s_gist' % (model._meta.db_table, f.column)
            clauses = [style.SQL_KEYWORD('CREATE INDEX'),
                style.SQL_TABLE(qn(truncate_name(index_name, self.connection.ops.max_name_length()))),
                style.SQL_KEYWORD('ON'),
                style.SQL_TABLE(qn(model._meta.db_table)),
                style.SQL_KEYWORD('USING GIST'),
                '(%s)' % style.SQL_FIELD(qn(f.column))]
            return ['%s%s;' % (' '.join(clauses), tablespace_sql)]
        else:
            return super(DatabaseCreation, self).sql_indexes_for_field(model, f, style)

class DatabaseWrapper(DatabaseWrapper):
    def __init__(self, *args, **params):
        super(DatabaseWrapper, self).__init__(*args, **params)
        self.creation = DatabaseCreation(self)
    def _cursor(self):
        cursor = super(DatabaseWrapper, self)._cursor()
        register_hstore(self.connection, globally=True)
        self._cursor = super(DatabaseWrapper, self)._cursor
        return cursor
