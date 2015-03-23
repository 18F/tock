import os

import dj_database_url

from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']  # proxied

STATIC_ROOT = '/app/tock/tock/static/'
STATIC_URL = '/tock/static/'

FORCE_SCRIPT_NAME = '/tock'

DATABASES = {}
DATABASES['default'] =  dj_database_url.config()

try:
    from .local_settings import *
except ImportError:
    pass
