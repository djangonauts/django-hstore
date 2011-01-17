
from django.db.backends.postgresql_psycopg2.base import *
from psycopg2.extras import register_hstore

class DatabaseWrapper(DatabaseWrapper):
    def _cursor(self):
        cursor = super(DatabaseWrapper, self)._cursor()
        register_hstore(self.connection, globally=True)
        self._cursor = super(DatabaseWrapper, self)._cursor
        return cursor

