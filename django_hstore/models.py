from django.db.backends.signals import connection_created
from django.db.backends.postgresql_psycopg2.base import DatabaseWrapper
from psycopg2.extras import register_hstore


def register_hstore_extension(sender, connection, *args, **kwargs):
    register_hstore(connection.connection, globally=True, unicode=True)
    cursor = connection.cursor()
    cursor.execute("CREATE EXTENSION IF NOT EXISTS hstore")
    connection.commit_unless_managed()

connection_created.connect(register_hstore_extension, sender=DatabaseWrapper)
