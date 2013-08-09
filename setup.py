from setuptools import setup, find_packages
from setuptools.command.test import test


class TestCommand(test):
    def run(self):
        from tests.runtests import runtests
        runtests()


setup(
    name='django-hstore',
    version='1.1.2',
    description="Support for PostgreSQL's hstore for Django.",
    long_description=open('README.rst').read(),
    author='Jann Kleen',
    author_email='jann@pocketvillage.com',
    license='BSD',
    url='https://github.com/pocketvillage/django-hstore',
    packages=find_packages(exclude=['tests', 'tests.*']),
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
