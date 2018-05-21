from django.utils.crypto import get_random_string

from .base import *  # noqa
# spell out explicit variable dependencies
from .base import (INSTALLED_APPS, MIDDLEWARE_CLASSES)

SECRET_KEY = get_random_string(50)

# Needed for CG Django UAA to leverage internal cloud.fake service
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tock-test',
        'HOST': 'localhost',
    }
}

# INSTALLED_APPS += ('nplusone.ext.django', )
# MIDDLEWARE_CLASSES += ('nplusone.ext.django.NPlusOneMiddleware', )
# NPLUSONE_WHITELIST = [
    # {'label': 'n_plus_one', 'model': 'hours.TimecardPrefillData'},
# ]
# NPLUSONE_RAISE = True

MEDIA_ROOT = './media/'

UAA_CLIENT_ID = 'testtesttesttesttesttesttesttesttesttesttest'
UAA_CLIENT_SECRET = 'testtesttesttesttesttesttesttesttesttest'
UAA_AUTH_URL = 'fake:'
UAA_TOKEN_URL = 'fake:'
