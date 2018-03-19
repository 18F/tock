import os

import dj_database_url

from .base import *  # noqa
# spell out explicit variable dependencies
from .base import DATABASES


USE_X_FORWARDED_HOST = True

ALLOWED_HOSTS = ['*']  # proxied

# FORCE_SCRIPT_NAME = '/tock'

STATIC_ROOT = '/app/tock/tock/static/'
STATIC_URL = '/tock/static/'

DATABASES['default'] = dj_database_url.config()

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
    },
}


try:
    from .local_settings import *     # noqa
except ImportError:
    pass
