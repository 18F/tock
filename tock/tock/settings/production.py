import os

import dj_database_url

from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']  # proxied

DATABASES = {}
DATABASES['default'] =  dj_database_url.config()

try:
    from .local_settings import *
except ImportError:
    pass
