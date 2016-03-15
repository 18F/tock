from .base import *  # noqa
import os

from django.utils.crypto import get_random_string

SECRET_KEY = get_random_string(50)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tock-test',
        'HOST': os.environ.get('DATABASE_HOST'),
        'USER': 'tock',
        'PASSWORD': 'tock',
    }
}

INSTALLED_APPS += ('nplusone.ext.django', )
MIDDLEWARE_CLASSES += ('nplusone.ext.django.NPlusOneMiddleware', )
NPLUSONE_RAISE = True

MEDIA_ROOT = './media/'
