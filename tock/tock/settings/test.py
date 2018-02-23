from django.utils.crypto import get_random_string

from .base import *  # noqa
# spell out explicit variable dependencies
from .base import (INSTALLED_APPS, MIDDLEWARE_CLASSES)

SECRET_KEY = get_random_string(50)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tock-test',
        'HOST': 'localhost',
    }
}

INSTALLED_APPS += ('nplusone.ext.django', )
MIDDLEWARE_CLASSES += ('nplusone.ext.django.NPlusOneMiddleware', )
NPLUSONE_RAISE = True

MEDIA_ROOT = './media/'
