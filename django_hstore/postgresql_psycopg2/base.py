
from django.db.backends.postgresql_psycopg2.base import *
from psycopg2.extras import register_hstore

class ExtendedDatabaseOperations(DatabaseOperations):
    def query_class(self, default):
        from django_hstore.query import Query
        return Query

class DatabaseWrapper(DatabaseWrapper):
    def __init__(self, *args, **params):
        super(DatabaseWrapper, self).__init__(*args, **params)
        self.features.uses_custom_query_class = True
        self.ops = ExtendedDatabaseOperations()
    def _cursor(self):
        cursor = super(DatabaseWrapper, self)._cursor()
        register_hstore(cursor)
        return cursor

