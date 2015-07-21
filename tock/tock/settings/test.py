from .base import *  # noqa

from django.utils.crypto import get_random_string

SECRET_KEY = get_random_string(50)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tock-test',
        'HOST': 'localhost',
    }
}

MEDIA_ROOT = './media/'
