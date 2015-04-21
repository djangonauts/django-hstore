Changelog
=========

Version 1.3.7 [unreleased]
--------------------------

- `9516dd7 <https://github.com/djangonauts/django-hstore/commit/9516dd77602aa27f189b0d633c1cefdd6090eb20>`_: Removed deprecated ``transaction.is_managed`` in favour of ``transaction.atomic`` for django >= 1.6
- `#103 <https://github.com/djangonauts/django-hstore/pull/103>`_: Fixed migration bug in ``VirtualField``

Version 1.3.6 [2015-04-10]
--------------------------

- `#80 <https://github.com/djangonauts/django-hstore/pull/80>`_: added ``SerializedDictionaryField``
- `#89 <https://github.com/djangonauts/django-hstore/pull/89>`_: avoided using jQuery global variable ``$`` in admin widget
- `#90 <https://github.com/djangonauts/django-hstore/issues/90>`_: added local copy of underscore.js
- `#92 <https://github.com/djangonauts/django-hstore/pull/92>`_: added workaround to handle none values in schema mode
- `#98 <https://github.com/djangonauts/django-hstore/pull/98>`_: fixed "don't force ``DatetimeField`` to ``utcnow()``" in schema mode
- `#100 <https://github.com/djangonauts/django-hstore/pull/100>`_: fixed "contains boolean bug" in query.py

Version 1.3.5 [2014-10-05]
--------------------------

- `#72 <https://github.com/djangonauts/django-hstore/pull/72>`_: automatic type casting in lookup queries
- `#74 <https://github.com/djangonauts/django-hstore/pull/74>`_: added ``isnull`` lookup to filter by is null on individual key/value pairs

Version 1.3.4 [2014-09-28]
--------------------------

- `#73 <https://github.com/djangonauts/django-hstore/issues/73>`_: added reload schema feature

Version 1.3.3 [2014-09-24]
--------------------------

- `#71 <https://github.com/djangonauts/django-hstore/issues/71>`_: empty ``HStoreDict.unicode()`` correctly returns ``{}``
- `#69 <https://github.com/djangonauts/django-hstore/issues/69>`_: ``HStoreField`` default value in case of ``null=True`` is empty ``HStoreDict`` instead of ``None``

Version 1.3.2 [2014-09-06]
--------------------------

- removed custom ``register_hstore`` function in favour of psycopg2 builtin one
- added hstore app bootstrapping in ``django_hstore.hstore``

Version 1.3.1 [2014-08-26]
--------------------------

- schema mode usage simplification
- `#57 <https://github.com/djangonauts/django-hstore/issues/57>`_: fixed schema mode compatibility with south migrations
- fixed compatibility with django 1.7 makemigrations command
- `#59 <https://github.com/djangonauts/django-hstore/issues/59>`_: ``get`` method of ``HStoreDict`` defaults to ``None``
- `#60 <https://github.com/djangonauts/django-hstore/issues/60>`_: added support for long integers
- minor improvements to support `django-rest-framework-hstore <https://github.com/djangonauts/django-rest-framework-hstore>`_ extension

Version 1.3.0 [2014-08-05]
--------------------------

- schema mode
- compare by multiple keys in comparison lookups (``lt``, ``gt``, ``lte``, ``gte``)

Version 1.2.5 [2014-06-28]
--------------------------

- introduced ``DJANGO_HSTORE_ADAPTER_REGISTRATION``
- `#45 <https://github.com/djangonauts/django-hstore/issues/45>`_: compatibility with SQLAlchemy
- `#44 <https://github.com/djangonauts/django-hstore/issues/44>`_: fixed ``unique_together`` bug
- `#46 <https://github.com/djangonauts/django-hstore/issues/46>`_: fixed admin widget error list
- fixed admin inline issue in django 1.6 default admin
- ``TabularInline`` is now explicitly unsupported

Version 1.2.4 [2014-06-18]
--------------------------

- ``HSTORE_GLOBAL_REGISTER`` setting
- added support for ``Decimal`` values

Version 1.2.3 [2014-04-17]
--------------------------

- added experimental compatibility with django 1.7
- psycopg2 backend fixes
- minor fixes to CSS of admin widget

Version 1.2.2 [2014-03-11]
--------------------------

- test runner improvements
- allow custom widgets
- updated docs with multidb settings (disable hstore on specific DBs)
- fixed ORM null filtering
- do not register HSTORE on non-postgresql DBs

Version 1.2.1 [2014-01-23]
--------------------------

- added Python3 support
- dropped automatic HStore registration
- fixed gis imports when geodjango is not installed

Version 1.2 [2014-01-04]
------------------------

- Fist release of 1.2.x series.
