import os

import dj_database_url

from .base import *

DEBUG = True

USE_X_FORWARDED_HOST = True

ALLOWED_HOSTS = ['*']  # proxied

FORCE_SCRIPT_NAME = '/tock'

STATIC_ROOT = '/app/tock/tock/static/'
STATIC_URL = FORCE_SCRIPT_NAME + '/static/'

DATABASES = {}
DATABASES['default'] =  dj_database_url.config()

try:
    from .local_settings import *
except ImportError:
    pass
