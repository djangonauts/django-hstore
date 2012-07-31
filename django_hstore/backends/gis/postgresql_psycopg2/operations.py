# -*- coding: utf-8 -*-
from django.contrib.gis.db.backends.postgis.operations import PostGISOperations

class DatabaseOperations(PostGISOperations):

    def _get_postgis_func(self, func, close=True):
        """
        Helper routine for calling PostGIS functions and returning their result.
        """
        cursor = self.connection._cursor()
        try:
            try:
                cursor.execute('SELECT %s()' % func)
                row = cursor.fetchone()
            except:
                # Responsibility of callers to perform error handling.
                raise
        finally:
            # Close out the connection.  See #9437.
            if close:
                self.connection.close()
        return row[0]

    def postgis_lib_version(self, close=True):
        "Returns the version number of the PostGIS library used with PostgreSQL."
        return self._get_postgis_func('postgis_lib_version', close)


    def postgis_version_tuple(self, close=True):
        """
        Returns the PostGIS version as a tuple (version string, major,
        minor, subminor).
        """
        # Getting the PostGIS version
        version = self.postgis_lib_version(close)
        m = self.version_regex.match(version)

        if m:
            major = int(m.group('major'))
            minor1 = int(m.group('minor1'))
            minor2 = int(m.group('minor2'))
        else:
            raise Exception('Could not parse PostGIS version string: %s' % version)

        return (version, major, minor1, minor2)

