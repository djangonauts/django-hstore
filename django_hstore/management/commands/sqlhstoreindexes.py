from optparse import make_option

from django import VERSION
from django.db.backends.utils import truncate_name
from django.core.management.base import AppCommand
from django.core.management.sql import sql_indexes
from django.db import connections, DEFAULT_DB_ALIAS, models


class Command(AppCommand):
    help = "Prints the CREATE INDEX SQL statements for hstore fields in the given model module name(s)."

    option_list = AppCommand.option_list + (
        make_option('--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS, help='Nominates a database to print the '
                'SQL for.  Defaults to the "default" database.'),

    )

    output_transaction = True

    def handle_app(self, app, **options):
        output = []
        connection = connections[options.get('database')]
        for model in models.get_models(app):
            if not model._meta.managed or model._meta.proxy:
                return []
            for f in model._meta.local_fields:
                kwargs = VERSION[:2] >= (1, 3) and {'connection': connection.creation.connection} or {}
                if f.db_type(**kwargs) == 'hstore':
                    output.extend(self.sql_indexes_for_field(connection.creation.connection, model, f, self.style))

        return u'\n'.join(output).encode('utf-8')

    def sql_indexes_for_field(self, connection, model, f, style):
        # create GIST index for hstore column
        qn = connection.ops.quote_name
        index_name = '%s_%s_gist' % (model._meta.db_table, f.column)
        clauses = [style.SQL_KEYWORD('CREATE INDEX'),
            style.SQL_TABLE(qn(truncate_name(index_name, connection.ops.max_name_length()))),
            style.SQL_KEYWORD('ON'),
            style.SQL_TABLE(qn(model._meta.db_table)),
            style.SQL_KEYWORD('USING GIST'),
            '(%s)' % style.SQL_FIELD(qn(f.column))]
        # add tablespace clause
        tablespace = f.db_tablespace or model._meta.db_tablespace
        if tablespace:
            sql = connection.ops.tablespace_sql(tablespace)
            if sql:
                clauses.append(sql)
        clauses.append(';')
        return [ ' '.join(clauses) ]