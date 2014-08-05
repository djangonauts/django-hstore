=============
django-hstore
=============

.. image:: https://travis-ci.org/djangonauts/django-hstore.png
   :target: https://travis-ci.org/djangonauts/django-hstore

.. image:: https://coveralls.io/repos/djangonauts/django-hstore/badge.png
  :target: https://coveralls.io/r/djangonauts/django-hstore

.. image:: https://landscape.io/github/djangonauts/django-hstore/master/landscape.png
   :target: https://landscape.io/github/djangonauts/django-hstore/master
   :alt: Code Health

.. image:: https://requires.io/github/djangonauts/django-hstore/requirements.png?branch=master
   :target: https://requires.io/github/djangonauts/django-hstore/requirements/?branch=master
   :alt: Requirements Status

.. image:: https://badge.fury.io/py/django-hstore.png
    :target: http://badge.fury.io/py/django-hstore

.. image:: https://pypip.in/d/django-hstore/badge.png
    :target: http://badge.fury.io/py/django-hstore

------------

You need **dynamic columns** in your tables. What do you do?

- Create lots of tables to handle it. Nice, now you’ll need more models and lots of additional sqls. Insertion and selection will be slow as hell.
- Use a **noSQL** database just for this issue. **Good luck**.
- Create a serialized column. Nice, insertion will be fine, and reading data from a record too. But, what if you have a condition in your select that includes serialized data? Yeah, regular expressions.

------------

Documentation_ - `Mailing List`_

.. _Documentation: http://djangonauts.github.io/django-hstore/
.. _`Mailing List`: https://groups.google.com/forum/#!forum/django-hstore
