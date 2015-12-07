How to properly sending bug reports
===================================

We review and fix bugs in our free time, which is a scarce resource.

That means that if you don't report the bug properly it may take months to verify and fix it.

A proper bug report should include:

* python version
* django version
* django-hstore version
* a high level procedure that explains how to reproduce the bug or a failing test case if it is a bug which is complex to reproduce

`See also guidelines on how to run the test suite <http://djangonauts.github.io/django-hstore/#_developers_guide>`_.

How to send a patch to fix a bug
================================

If you think you found a bug, you must first ensure it's reproduce in the test suite.

Patches without failing tests won't be accepted.

Avoid multiple commits and ensure the commit message is clear.

`See also guidelines on how to run the test suite <http://djangonauts.github.io/django-hstore/#_developers_guide>`_.

Things to avoid
===============

Do not create a separate project to explain the bug, that is worse than useless, it only gives us headaches and wastes our time.

Thank you
=========

Thank you for taking the time to read these guidelines.
