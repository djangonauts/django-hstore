# -*- coding: utf-8 -*-
from django import VERSION
from django.conf import settings
from django.db.backends.util import truncate_name
from django.contrib.gis.db.backends.postgis.base import PostGISCreation
from django.contrib.gis.db.models import GeometryField


class DatabaseCreation(PostGISCreation):

    def sql_table_creation_suffix(self):
        qn = self.connection.ops.quote_name
        return ' TEMPLATE %s' % qn(getattr(settings, 'POSTGIS_TEMPLATE', 'template_postgis'))

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
            output = []
            if isinstance(f, GeometryField):
                gqn = self.connection.ops.geo_quote_name
                qn = self.connection.ops.quote_name
                db_table = model._meta.db_table

                if f.geography:
                    # Geogrophy columns are created normally.
                    pass
                else:
                    # Geometry columns are created by `AddGeometryColumn`
                    # stored procedure.
                    output.append(style.SQL_KEYWORD('SELECT ') +
                                  style.SQL_TABLE('AddGeometryColumn') + '(' +
                                  style.SQL_TABLE(gqn(db_table)) + ', ' +
                                  style.SQL_FIELD(gqn(f.column)) + ', ' +
                                  style.SQL_FIELD(str(f.srid)) + ', ' +
                                  style.SQL_COLTYPE(gqn(f.geom_type)) + ', ' +
                                  style.SQL_KEYWORD(str(f.dim)) + ');')

                if not f.null:
                    # Add a NOT NULL constraint to the field
                    output.append(style.SQL_KEYWORD('ALTER TABLE ') +
                                  style.SQL_TABLE(qn(db_table)) +
                                  style.SQL_KEYWORD(' ALTER ') +
                                  style.SQL_FIELD(qn(f.column)) +
                                  style.SQL_KEYWORD(' SET NOT NULL') + ';')

                if f.spatial_index:
                    # Spatial indexes created the same way for both Geometry and
                    # Geography columns
                    if f.geography:
                        index_opts = ''
                    else:
                        '''
                        Due this ``https://code.djangoproject.com/ticket/16455``,
                        checking postgis version for adding (or not adding) index
                        options on creating spatial index
                        '''
                        postgis_version = self.connection.ops.postgis_version_tuple(close=False)[1:]

                        if postgis_version >= (2, 0):
                            index_opts = ''
                        else:
                            index_opts = ' ' + style.SQL_KEYWORD(self.geom_index_opts)

                    output.append(style.SQL_KEYWORD('CREATE INDEX ') +
                                  style.SQL_TABLE(qn('%s_%s_id' % (db_table, f.column))) +
                                  style.SQL_KEYWORD(' ON ') +
                                  style.SQL_TABLE(qn(db_table)) +
                                  style.SQL_KEYWORD(' USING ') +
                                  style.SQL_COLTYPE(self.geom_index_type) + ' ( ' +
                                  style.SQL_FIELD(qn(f.column)) + index_opts + ' );')
                return output
            else:
                return super(DatabaseCreation, self).sql_indexes_for_field(model, f, style)
