=============
django-hstore
=============

.. image:: https://travis-ci.org/djangonauts/django-hstore.svg
   :target: https://travis-ci.org/djangonauts/django-hstore

.. image:: https://coveralls.io/repos/djangonauts/django-hstore/badge.svg
  :target: https://coveralls.io/r/djangonauts/django-hstore

.. image:: https://requires.io/github/djangonauts/django-hstore/requirements.svg?branch=master
   :target: https://requires.io/github/djangonauts/django-hstore/requirements/?branch=master
   :alt: Requirements Status

.. image:: https://badge.fury.io/py/django-hstore.svg
    :target: https://pypi.python.org/pypi/django-hstore

.. image:: https://img.shields.io/pypi/dm/django-hstore.svg
   :target: https://pypi.python.org/pypi/django-hstore

------------

You need **dynamic columns** in your tables. What do you do?

- Create lots of tables to handle it. Nice, now you'll need more models and lots of additional sqls. Insertion and selection will be slow as hell.
- Use a **noSQL** database just for this issue. **Good luck**.
- Create a serialized column. Nice, insertion will be fine, and reading data from a record too. But, what if you have a condition in your select that includes serialized data? Yeah, regular expressions.

------------

Documentation_ - `Mailing List`_

.. _Documentation: http://djangonauts.github.io/django-hstore/
.. _`Mailing List`: https://groups.google.com/forum/#!forum/django-hstore

------------

Projects using this package
---------------------------

- `django-rest-framework-hstore <https://github.com/djangonauts/django-rest-framework-hstore>`__: **django-rest-framework** tools for **django-hstore**
- `Nodeshot <https://github.com/ninuxorg/nodeshot>`__: extensible django web application for management of community-led georeferenced data - some features of **django-hstore**, like the ``schema-mode`` have been developed for this project
