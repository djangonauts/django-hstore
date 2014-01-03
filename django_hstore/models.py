from django.db.backends.signals import connection_created
from django.db.backends.postgresql_psycopg2.base import DatabaseWrapper
from django.contrib.gis.db.backends.postgis.base import DatabaseWrapper as GeoDatabaseWrapper

from .utils import register_hstore


def register_hstore_extension(sender, connection, *args, **kwargs):
    # create hstore extension if it doesn't exist
    # experimental
    cursor = connection.cursor()
    cursor.execute("CREATE EXTENSION IF NOT EXISTS hstore")
    try:
        connection.connection.commit_unless_managed()
    # it seems django 1.6 does not have this attribute anymore
    # probably due to changes to the transaction internals
    except AttributeError:
        pass
    # register hstore extension
    register_hstore(connection.connection, globally=True, unicode=True)


# register hstore field on DB connection for postgresql_psycopg2
connection_created.connect(register_hstore_extension, sender=DatabaseWrapper)

# register hstore field on DB connection for postgis
connection_created.connect(register_hstore_extension, sender=GeoDatabaseWrapper)
