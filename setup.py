from setuptools import setup, find_packages
from setuptools.command.test import test
from setuptools import setup
import re
import os
import sys

from django_hstore import get_version


class TestCommand(test):
    def run(self):
        from tests.runtests import runtests
        runtests()


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}

setup(
    name='django-hstore',
    version=get_version(),
    description="Support for PostgreSQL's hstore for Django.",
    long_description=open('README.rst').read(),
    author='Federico Capoano (nemesisdesign)',
    license='BSD',
    url='https://github.com/nemesisdesign/django-hstore',
    packages=get_packages('django_hstore'),
    package_data=get_package_data('django_hstore'),
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Framework :: Django',
    ],
    cmdclass={"test": TestCommand},
)
