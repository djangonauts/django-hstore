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

            # create GIST index for hstore columne
            qn = self.connection.ops.quote_name
            index_name = '%s_%s_gist' % (model._meta.db_table, f.column)
            clauses = [style.SQL_KEYWORD('CREATE INDEX'),
                style.SQL_TABLE(qn(truncate_name(index_name, self.connection.ops.max_name_length()))),
                style.SQL_KEYWORD('ON'),
                style.SQL_TABLE(qn(model._meta.db_table)),
                style.SQL_KEYWORD('USING GIST'),
                '(%s)' % style.SQL_FIELD(qn(f.column))]

            # add tablespace clause
            tablespace = f.db_tablespace or model._meta.db_tablespace
            if tablespace:
                sql = self.connection.ops.tablespace_sql(tablespace)
                if sql:
                    clauses.append(sql)
            clauses.append(';')
            return [ ' '.join(clauses) ]
        return super(DatabaseCreation, self).sql_indexes_for_field(model, f, style)


class DatabaseWrapper(DatabaseWrapper):
    """Custom DB wrapper to inject connection registration and DB creation code"""

    def __init__(self, *args, **params):
        super(DatabaseWrapper, self).__init__(*args, **params)
        self.creation = DatabaseCreation(self)

    def _cursor(self):
        # ensure that we're connected
        cursor = super(DatabaseWrapper, self)._cursor()

        # register hstore extension
        register_hstore(self.connection, globally=True, unicode=True)

        # bypass future registrations
        self._cursor = super(DatabaseWrapper, self)._cursor
        return cursor
