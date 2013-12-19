
DATABASES = {
    'default': {
        # possible backends are:
        #   * django.db.backends.postgresql_psycopg2
        #   * django.contrib.gis.db.backends.postgis
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'django_hstore',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': '',
        'PORT': ''
    },
}