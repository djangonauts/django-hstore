=============
django-hstore
=============

Django-hstore is a niche library which integrates the `hstore`_ extension of
PostgreSQL into Django.

Dependencies:

 * **Django 1.2+**
 * **PostgreSQL 9.0+**
 * **Psycopg 2.3+**.

=============
Fork features
=============

This fork aims to support spatial querysets. Now supported only Postgis backend.

Limitations
===========

- Due to how Django implements its ORM, you will need to use the custom
  ``postgresql_psycopg2`` or ``postgis`` backend defined in this package,
  which naturally will prevent you from dropping in other django extensions
  which require a custom backend (unless you fork and combine).
- PostgreSQL's implementation of hstore has no concept of type; it stores a
  mapping of string keys to string values. This library makes no attempt to
  coerce keys or values to strings.

Running the tests
=================

Assuming one has the dependencies installed, and a **PostgreSQL 9.0+** server up and
running::

    python setup.py test

You might need to tweak the DB settings according to your DB configuration.
You can copy the file settings.py and create **local_settings.py**, which will
be used instead of the default settings.py.

If after running this command you get an **error** saying::
    
    type "hstore" does not exist

Try this::

    psql template1 -c 'create extension hstore;'

More details here: `PostgreSQL error type hstore does not exist`_

Usage
=====

First, update your settings module to specify the custom database backend::

    DATABASES = {
        'default': {
            'ENGINE': 'django_hstore.backends.postgresql_psycopg2',
            # or
            # 'ENGINE': 'django_hstore.backends.postgis',
            ...
        }
    }

**Note to South users:** If you keep getting errors like `There is no South
database module 'south.db.None' for your database.`, add the following to
`settings.py`::

    SOUTH_DATABASE_ADAPTERS = {'default': 'south.db.postgresql_psycopg2'}

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


Model definition is straightforward::

    from django.db import models
    from django_hstore import hstore

    class Something(models.Model):
        name = models.CharField(max_length=32)
        data = hstore.DictionaryField()
        
        objects = hstore.HStoreManager()
        # or objects = hstore.HStoreGeoManager()

        def __unicode__(self):
            return self.name

You then treat the ``data`` field as simply a dictionary of string pairs::

    instance = Something.objects.create(name='something', data={'a': '1', 'b': '2'})
    assert instance.data['a'] == '1'

    empty = Something.objects.create(name='empty')
    assert empty.data == {}

    empty.data['a'] = '1'
    empty.save()
    assert Something.objects.get(name='something').data['a'] == '1'

Booleans, integers, floats, lists and dictionaries will be converted to strings.
Lists, dictionaries and booleans are converted into JSON formatted strings, so
can be decoded if needed.

    instance = Something.objects.create(name='something', data={'int': 1, 'bool': True})
    
    instance.data['int'] == '1'
    instance.data['bool'] == 'true'
    
    import json
    instance.data['dict'] = { 'list': ['a', False, 1] }
    instance.data['dict'] == '{"list": ["a", false, 1]}'
    json.loads(instance.data['dict']) == { 'list': ['a', False, 1] }
    >>> True

You can issue indexed queries against hstore fields::

    # equivalence
    Something.objects.filter(data={'a': '1', 'b': '2'})

    # comparision
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
will be converted to text and the lookup will be performed on all the keys and all the values::

    Something.objects.create(data={ 'some_key': 'some crazy Value' })

    # classic text lookup (look up for occurence of string in all the keys)
    Something.objects.filter(data__contains='crazy')
    Something.objects.filter(data__contains='some_key')
    # classic case insensitive text looup
    Something.objects.filter(data__icontains='value')
    Something.objects.filter(data__icontains='SOME_KEY')

You can also take advantage of some db-side functionality by using the manager::

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

.. _hstore: http://www.postgresql.org/docs/9.1/interactive/hstore.html
.. _PostgreSQL error type hstore does not exist: http://clarkdave.net/2012/09/postgresql-error-type-hstore-does-not-exist/