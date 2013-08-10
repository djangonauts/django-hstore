
DATABASES = {
    'default': {
        'ENGINE': 'django_hstore.backends.postgis',
        'NAME': 'django_hstore',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': '',
        'PORT': ''
        },
    }