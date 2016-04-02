Changelog
=========

Version 1.4.2 [2016-04-02]
--------------------------

- `#144 <https://github.com/djangonauts/django-hstore/issues/144>`_: fixed 1.4.1 regression: "TypeError: Decimal is not JSON serializable"
- `#147 <https://github.com/djangonauts/django-hstore/pull/147>`_: fixed version comparison (broken for django 1.10)
- `#148 <https://github.com/djangonauts/django-hstore/issues/148>`_: fixed broken image "src" for icons in admin for Django >= 1.9

Version 1.4.1 [2015-12-07]
--------------------------

- `#140 <https://github.com/djangonauts/django-hstore/pull/140>`_: added support for django 1.9
- `#139 <https://github.com/djangonauts/django-hstore/pull/139>`_: dropped support for django 1.6 and python 2.6
- `#128 <https://github.com/djangonauts/django-hstore/pull/128>`_: added ``CONNECTION_CREATED_SIGNAL_WEAKREF``

Version 1.4.0 [2015-06-28]
--------------------------

- `#107 <https://github.com/djangonauts/django-hstore/pull/107>`_: added support for django 1.8
- `#121 <https://github.com/djangonauts/django-hstore/pull/121>`_: fixed "value not assignment" in forms.py
- `#117 <https://github.com/djangonauts/django-hstore/pull/117>`_: fixed makemigrations bug with django 1.8
- `#118 <https://github.com/djangonauts/django-hstore/issues/118>`_: improved reload_schema for django 1.8
- `#111 <https://github.com/djangonauts/django-hstore/issues/111>`_: fixed bug in create manager method when using ``SerializedDictionaryField``

Version 1.3.8 [2015-06-07]
--------------------------

- `#110 <https://github.com/djangonauts/django-hstore/pull/110>`_: change ``id`` to ``pk`` on ``model_instance`` check

Version 1.3.7 [2015-04-24]
--------------------------

- `9516dd7 <https://github.com/djangonauts/django-hstore/commit/9516dd77602aa27f189b0d633c1cefdd6090eb20>`_: Removed deprecated ``transaction.is_managed`` in favour of ``transaction.atomic`` for django >= 1.6
- `eeda0e5 <https://github.com/djangonauts/django-hstore/commit/eeda0e50caa9107189961f97a4f4e7a234aa7fc9>`_: Removed import for django <= 1.3 in query.py
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
