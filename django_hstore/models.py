from django.db.backends.signals import connection_created
try:
    from django.db.backends.postgresql_psycopg2.base import DatabaseWrapper
    from .util import register_hstore

    def register_hstore_extension(sender, connection, *args, **kwargs):
        cursor = connection.cursor()
        cursor.execute("CREATE EXTENSION IF NOT EXISTS hstore")
        connection.commit_unless_managed()
        register_hstore(connection.connection, globally=True, unicode=True)

    connection_created.connect(register_hstore_extension, sender=DatabaseWrapper)
except ImportError:
    pass
