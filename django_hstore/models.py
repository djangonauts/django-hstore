import sys

from django.db.backends.signals import connection_created

from .utils import register_hstore


class ConnectionCreateHandler(object):
    """
    Generic connection handlers manager.
    Executes attached functions when connection is created.
    With possibility of attaching single execution methods.
    """

    generic_handlers = []
    unique_handlers = []

    def __call__(self, sender, connection, **kwargs):
        handlers = set()

        if len(self.unique_handlers) > 0:
            handlers.update(self.unique_handlers)
            self.unique_handlers = []

        handlers.update(self.generic_handlers)

        # List comprehension is used instead of for statement
        # only for performance.
        [x(connection) for x in handlers]

    def attach_handler(self, func, vendor=None, unique=False):
        if unique:
            self.unique_handlers.append(func)
        else:
            self.generic_handlers.append(func)


connection_handler = ConnectionCreateHandler()
connection_created.connect(connection_handler, dispatch_uid="_connection_create_handler")


def register_hstore_handler(connection, **kwargs):
    # do not register hstore if DB is not postgres
    # do not register if HAS_HSTORE flag is set to false
    if connection.vendor != 'postgresql' or connection.settings_dict.get('HAS_HSTORE', True) is False:
        return

    if sys.version_info[0] < 3:
        register_hstore(connection.connection, globally=True, unicode=True)
    else:
        register_hstore(connection.connection, globally=True)

connection_handler.attach_handler(register_hstore_handler, vendor="postgresql", unique=True)