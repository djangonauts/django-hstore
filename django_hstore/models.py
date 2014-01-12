import sys

from django.db.backends.signals import connection_created
from django.db.backends.postgresql_psycopg2.base import DatabaseWrapper
from django.contrib.gis.db.backends.postgis.base import DatabaseWrapper as GeoDatabaseWrapper

from .utils import register_hstore


class ConnectionCreateHandler(object):
    """
    Generic connection handlers manager.
    Executes attrached funcitions on connection is created.
    With facilty of attaching single execution methods.
    """

    generic_handlers = {}
    unique_handlers = {}

    def __call__(self, sender, connection, **kwargs):
        handlers = set()
        if None in self.unique_handlers:
            handlers.update(self.unique_handlers[None])
            del self.unique_handlers[None]

        if connection.vendor in self.unique_handlers:
            handlers.update(self.unique_handlers[connection.vendor])
            del self.unique_handlers[connection.vendor]

        if connection.vendor in self.generic_handlers:
            handlers.update(self.generic_handlers[connection.vendor])

        [x(connection) for x in handlers]

    def attach_handler(self, func, vendor=None, unique=False):
        if unique:
            if vendor not in self.unique_handlers:
                self.unique_handlers[vendor] = [func]
            else:
                self.unique_handlers[vendor].append(func)

        else:
            if vendor not in self.generic_handlers:
                self.generic_handlers[vendor] = [func]
            else:
                self.generic_handlers[vendor].append(func)


connection_handler = ConnectionCreateHandler()
connection_created.connect(connection_handler, attach_handler,
                           dispatch_uid="_connection_create_handler")


def register_hstore_handler(connection, **kwargs):
    if not connection.settings_dict.get('HAS_HSTORE', True):
        return

    if sys.version_info[0] < 3:
        register_hstore(connection.connection, globally=True, unicode=True)
    else:
        register_hstore(connection.connection, globally=True)

connection_handler.attach_handler(register_hstore_handler, vendor="postgresql", unique=True)


# def register_hstore_extension(sender, connection, *args, **kwargs):
#     # register hstore extension
#     register_hstore(connection.connection, globally=True, unicode=True)
#
# # register hstore field on DB connection for postgresql_psycopg2
# connection_created.connect(register_hstore_extension, sender=DatabaseWrapper,
#                            dispatch_uid="_register_hstore")
#
# # register hstore field on DB connection for postgis
# connection_created.connect(register_hstore_extension, sender=GeoDatabaseWrapper,
#                            dispatch_uid="_register_hstore_gis")
