
DATABASES = {
    'default': {
        'ENGINE': 'django_hstore.backends.gis.postgresql_psycopg2',
        'NAME': 'django_hstore_test',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432'
        },
    }

INSTALLED_APPS = ['tests.app',]
