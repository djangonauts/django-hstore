from distutils.core import setup

setup(
    name='django-hstore',
    version='1.0.0',
    description="Support for PostgreSQL's hstore for Django.",
    long_description=open('README.rst').read(),
    author='Jordan McCoy',
    author_email='mccoy.jordan@gmail.com',
    license='BSD',
    url='http://github.com/jordanm/django-hstore',
    packages=[
        'django_hstore',
        'django_hstore.backends.postgresql_psycopg2',
        'django_hstore.backends.gis.postgresql_psycopg2',
    ],
)
