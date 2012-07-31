from psycopg2.extras import register_hstore

from django.contrib.gis.db.backends.postgis.base import PostGISIntrospection, \
    DatabaseWrapper as PostGISWrapper
from django_hstore.backends.gis.postgresql_psycopg2.creation import DatabaseCreation
from django_hstore.backends.gis.postgresql_psycopg2.operations import DatabaseOperations


class DatabaseWrapper(PostGISWrapper):
    def __init__(self, *args, **params):
        super(DatabaseWrapper, self).__init__(*args, **params)
        self.creation = DatabaseCreation(self)
        self.ops = DatabaseOperations(self)
        self.introspection = PostGISIntrospection(self)

    def _cursor(self):
        cursor = super(DatabaseWrapper, self)._cursor()
        register_hstore(self.connection, globally=True)
        self._cursor = super(DatabaseWrapper, self)._cursor
        return cursor
