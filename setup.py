from setuptools import setup, find_packages
import re
import os
import sys

from django_hstore import get_version


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
    description="Bring schemaless PostgreSQL (HStore) in Django",
    long_description=open('README.rst').read(),
    author='Jordan McCoy',
    maintainer='Djangonauts Organization',
    maintainer_email='django-hstore@googlegroups.com',
    license='BSD',
    url='https://github.com/djangonauts/django-hstore',
    download_url='https://github.com/djangonauts/django-hstore/releases',
    platforms=['Platform Indipendent'],
    keywords=['django', 'hstore', 'schemaless'],
    packages=get_packages('django_hstore'),
    package_data=get_package_data('django_hstore'),
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Framework :: Django',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
