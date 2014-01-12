=============
django-hstore
=============

.. image:: https://travis-ci.org/djangonauts/django-hstore.png
   :target: https://travis-ci.org/djangonauts/django-hstore

.. image:: https://coveralls.io/repos/djangonauts/django-hstore/badge.png
  :target: https://coveralls.io/r/djangonauts/django-hstore

Django-hstore is a niche library which integrates the `hstore`_ extension of
PostgreSQL into Django.

Mailing List: https://groups.google.com/forum/#!forum/django-hstore

Dependencies:

* **Django 1.4, 1.5 and 1.6**
* **PostgreSQL 9.0+**
* **Psycopg 2.3+**.

Extras:

* **Postgis compatibility**
* usable **admin widget**
* nice admin widget for **django-grappelli**

admin widget screenshot:

.. figure:: https://raw.github.com/djangonauts/django-hstore/master/docs/deafult-admin-widget.png

grappelli admin widget screenshot:

.. figure:: https://raw.github.com/djangonauts/django-hstore/master/docs/hstore-widget.png

===========
Limitations
===========

* PostgreSQL's implementation of hstore has no concept of type; it stores a
  mapping of string keys to string values. Values are stored as strings in the
  database regarding of their original type.
* Hstore extension is not automatically installed on use this package. You must install it manually.
* To run tests, hstore extension must be installed on template1 database.

=======
Install
=======

Install using pip (you need git) by running:

.. code-block:: bash

    pip install -e git+git://github.com/djangonauts/django-hstore#egg=django-hstore

=====
Setup
=====

First, add **django_hstore** to your `settings.INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_hstore',
        ..
    )

Second, collect static files (needed for the admin widget) with:

.. code-block:: bash

    python manage.py collectstatic

===========================
Upgrade from older versions
===========================

In **version 1.2.x** some internals have been changed in order to simplify usage and prevent errors.

Values are automatically converted to strings, fields costantly validate input and so on.

If you are upgrading from an older version ensure your application code works as expected. If it doesn't you will either have to update your code or tie your application's requirement to the older version of django-hstore (1.1.1).

===================
Note to South users
===================

If you keep getting errors like `There is no South
database module 'south.db.None' for your database.`, add the following to
`settings.py`:

.. code-block:: python

    SOUTH_DATABASE_ADAPTERS = {'default': 'south.db.postgresql_psycopg2'}

============
Admin widget
============

django-hstore ships a nice admin widget that makes the field more user-friendly.

.. figure:: https://raw.github.com/djangonauts/django-hstore/master/docs/deafult-admin-widget.png

Each time a key or a value is modified the underlying textarea is updated:

.. figure:: https://raw.github.com/djangonauts/django-hstore/master/docs/deafult-admin-widget-raw.png

======================
Grappelli Admin widget
======================

If you use the awsome `django-grappelli`_ there's an even nicer looking widget for you too!

.. figure:: https://raw.github.com/djangonauts/django-hstore/master/docs/hstore-widget.png

Each time a key or a value is modified the underlying textarea is updated:

.. figure:: https://raw.github.com/djangonauts/django-hstore/master/docs/hstore-widget-raw.png

=====
Usage
=====

The library provides three principal classes:

``django_hstore.hstore.DictionaryField``
    An ORM field which stores a mapping of string key/value pairs in an hstore
    column.
``django_hstore.hstore.ReferencesField``
    An ORM field which builds on DictionaryField to store a mapping of string
    keys to django object references, much like ForeignKey.
``django_hstore.hstore.HStoreManager``
    An ORM manager which provides much of the query functionality of the
    library.
``django_hstore.hstore.HStoreGeoManager``
    An additional ORM manager to provide Geodjango functionality as well.

------------
Model fields
------------

Model definition is straightforward:

.. code-block:: python

    from django.db import models
    from django_hstore import hstore

    class Something(models.Model):
        name = models.CharField(max_length=32)
        data = hstore.DictionaryField()  # can pass attributes like null, blank, ecc.

        objects = hstore.HStoreManager()
        # IF YOU ARE USING POSTGIS:
        # objects = hstore.HStoreGeoManager()

ReferenceField model field is also straightforward:

.. code-block:: python

    class ReferenceContainer(models.Model):
        name = models.CharField(max_length=32)
        refs = hstore.ReferencesField()

        objects = hstore.HStoreManager()

----------
Python API
----------

You then treat the ``data`` field as simply a dictionary of string pairs:

.. code-block:: python

    instance = Something.objects.create(name='something', data={'a': '1', 'b': '2'})
    assert instance.data['a'] == '1'

    empty = Something.objects.create(name='empty')
    assert empty.data == {}

    empty.data['a'] = '3'
    empty.save()
    assert Something.objects.get(name='empty').data['a'] == '3'

Booleans, integers, floats, lists and dictionaries will be converted to strings.
Lists, dictionaries and booleans are converted into JSON formatted strings, so
can be decoded if needed:

.. code-block:: python

    instance = Something.objects.create(name='something', data={'int': 1, 'bool': True})

    instance.data['int'] == '1'
    instance.data['bool'] == 'true'

    import json
    instance.data['dict'] = { 'list': ['a', False, 1] }
    instance.data['dict'] == '{"list": ["a", false, 1]}'
    json.loads(instance.data['dict']) == { 'list': ['a', False, 1] }
    >>> True

You can issue indexed queries against hstore fields:

.. code-block:: python

    # equivalence
    Something.objects.filter(data={'a': '1', 'b': '2'})

    # comparison (greater than, less than or equal to, ecc)
    Something.objects.filter(data__gt={'a': '1'})
    Something.objects.filter(data__gte={'a': '1'})
    Something.objects.filter(data__lt={'a': '2'})
    Something.objects.filter(data__lte={'a': '2'})

    # subset by key/value mapping
    Something.objects.filter(data__contains={'a': '1'})

    # subset by list of some key values
    Something.objects.filter(data__contains={'a': ['1', '2']})

    # subset by list of keys
    Something.objects.filter(data__contains=['a', 'b'])

    # subset by single key
    Something.objects.filter(data__contains=['a'])

You can still do classic django "contains" lookups as you would normally do for normal text
fields if you were looking for a particular string. In this case, the HSTORE field
will be converted to text and the lookup will be performed on all the keys and all the values:

.. code-block:: python

    Something.objects.create(data={ 'some_key': 'some crazy Value' })

    # classic text lookup (look up for occurence of string in all the keys)
    Something.objects.filter(data__contains='crazy')
    Something.objects.filter(data__contains='some_key')
    # classic case insensitive text looup
    Something.objects.filter(data__icontains='value')
    Something.objects.filter(data__icontains='SOME_KEY')

--------------
HSTORE manager
--------------

You can also take advantage of some db-side functionality by using the manager:

.. code-block:: python

    # identify the keys present in an hstore field
    >>> Something.objects.hkeys(id=instance.id, attr='data')
    ['a', 'b']

    # peek at a a named value within an hstore field
    >>> Something.objects.hpeek(id=instance.id, attr='data', key='a')
    '1'

    # do the same, after filter
    >>> Something.objects.filter(id=instance.id).hpeek(attr='data', key='a')
    '1'

    # remove a key/value pair from an hstore field
    >>> Something.objects.filter(name='something').hremove('data', 'b')

The hstore methods on manager pass all keyword arguments aside from ``attr`` and
``key`` to ``.filter()``.

--------------------
ReferenceField Usage
--------------------

**ReferenceField** is a field that allows to reference other database objects
without using a classic ManyToMany relationship.

Here's an example with the `ReferenceContainer` model defined in the **Model fields** section:

.. code-block:: python

    r = ReferenceContainer(name='test')
    r.refs['another_object'] = AnotherModel.objects.get(slug='another-object')
    r.refs['some_object'] = AnotherModel.objects.get(slug='some-object')
    r.save()

    r = ReferenceContainer.objects.get(name='test')
    r.refs['another_object']
    '<AnotherModel: AnotherModel object>'
    r.refs['some_object']
    '<AnotherModel: AnotherModel some_object>'

The database is queried only when references are accessed directly.
Once references have been retrieved they will be stored for any eventual subsequent access:

.. code-block:: python

    r = ReferenceContainer.objects.get(name='test')
    # this won't query the database
    r.refs
    { u'another_object': u'myapp.models.AnotherModel:1', u'some_object': u'myapp.models.AnotherModel:2' }

    # this will query the database
    r.refs['another_object']
    '<AnotherModel: AnotherModel object>'

    # retrieved reference is now visible also when calling the HStoreDict object:
    r.refs
    { u'another_object': <AnotherModel: AnotherModel object>, u'some_object': u'myapp.models.AnotherModel:2' }

=================
Running the tests
=================

Assuming one has the dependencies installed, and a **PostgreSQL 9.0+** server up and
running:

.. code-block:: bash

    python setup.py test

You might need to tweak the DB settings according to your DB configuration.
You can copy the file settings.py and create **local_settings.py**, which will
be used instead of the default settings.py.

If after running this command you get an **error** saying::

    type "hstore" does not exist

Try this:

.. code-block:: bash

    psql template1 -c 'create extension hstore;'

More details here: `PostgreSQL error type hstore does not exist`_

.. _hstore: http://www.postgresql.org/docs/9.1/interactive/hstore.html
.. _PostgreSQL error type hstore does not exist: http://clarkdave.net/2012/09/postgresql-error-type-hstore-does-not-exist/
.. _django-grappelli: http://grappelliproject.com/

=================
How to contribute
=================

1. Join the mailing List: `django-hstore mailing list`_ and announce your intentions
2. Follow `PEP8, Style Guide for Python Code`_
3. Fork this repo
4. Write code
5. Write tests for your code
6. Ensure all tests pass
7. Ensure test coverage is not under 90%
8. Document your changes
9. Send pull request

.. _PEP8, Style Guide for Python Code: http://www.python.org/dev/peps/pep-0008/
.. _django-hstore mailing list: https://groups.google.com/forum/#!forum/django-hstore


.. image:: https://d2weczhvl823v0.cloudfront.net/djangonauts/django-hstore/trend.png
   :target: https://bitdeli.com/free
