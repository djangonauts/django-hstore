from django.conf import settings
from django.core.management import call_command
from os import environ


settings.configure(
    HSTORE_SQL = environ.get('HSTORE_SQL',None),
    DATABASES = {
        'default': {
            'ENGINE': 'django_hstore.postgresql_psycopg2',
            'NAME': environ['DB_NAME'],
            'USER': environ['DB_USER'],
        }
    },
    INSTALLED_APPS = ['tests.app']
)

call_command('syncdb')

