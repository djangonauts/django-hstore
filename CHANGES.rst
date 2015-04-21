Changelog
=========

Version 1.3.7 [unreleased]
--------------------------

- #103: Fixed VirtualField migration bug

Version 1.3.6 [2015-04-10]
--------------------------

- #80: added SerializedDictionaryField
- #89: avoided using javascript global variable "$" in admin widget
- #90: added local copy of underscore.js
- #92: added workaround to handle none values in schema mode
- #98: fixed "don't force DatetimeField to utcnow()" in schema mode
- #100: fixed "contains boolean bug" in query.py

Version 1.3.5 [2014-10-05]
--------------------------

- #72: automatic type casting in lookup queries
- #74: added "isnull" lookup to filter by is null on individual key/value pairs

Version 1.3.4 [2014-09-28]
--------------------------

- #73: added reload schema feature

Version 1.3.3 [2014-09-24]
--------------------------

- #71: empty HStoreDict.unicode() correctly returns '{}'
- #69: HStoreField default value in case of null=True is empty HStoreDict instead of None

Version 1.3.2 [2014-09-06]
--------------------------

- removed custom register_hstore function in favour of psycopg2 builtin one
- added hstore app bootstrapping in django_hstore.hstore

Version 1.3.1 [2014-08-26]
--------------------------

- schema mode usage simplification
- #57: fixed schema mode compatibility with south migrations
- fixed compatibility with django 1.7 makemigrations command
- #59: HStoreDict get method defaults to None
- #60: added support for long integers
- minor improvements to support django-rest-framework-hstore extension

Version 1.3.0 [2014-08-05]
--------------------------

- schema mode
- compare by multiple keys in comparison lookups (lt, gt, lte, gte)

Version 1.2.5 [2014-06-28]
--------------------------

- introduced DJANGO_HSTORE_ADAPTER_REGISTRATION
- #45: compatibility with SQLAlchemy
- #44: fixed unique_together clause
- #46: fixed admin widget error list
- fixed admin inline issue in django 1.6 default admin
- TabularInline is now explicitly unsupported

Version 1.2.4 [2014-06-18]
--------------------------

- HSTORE_GLOBAL_REGISTER setting
- added support for Decimal values

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
