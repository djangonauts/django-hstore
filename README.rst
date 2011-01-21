=============
django-hstore
=============

Django-hstore is a niche library which integrates the `hstore`_ extension of PostgreSQL into Django,
assuming one is using Django 1.2+, PostgreSQL 9.0+, and Psycopg 2.3+.

Running the tests
=================

Assuming one has the dependencies installed as well as nose, and a PostgreSQL 9.0+ server up and running::

    DB_USER=<username> HSTORE_SQL=<path-to-contrib/hstore.sql> ./runtests

.. _hstore: http://www.postgresql.org/docs/9.0/interactive/hstore.html
