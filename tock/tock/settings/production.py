import os

import dj_database_url

from .base import *  # noqa
# spell out explicit variable dependencies
from .base import DATABASES

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

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
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] "
                      "%(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S",
        },
        'simple': {
            'format': "%(levelname)s %(message)s",
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/tock.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'propagate': True,
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
        'django.template': {
            'handlers': ['console', 'file'],
            'propagate': True,
            'level': 'INFO',
        },
        'uaa_client': {
            'handlers': ['console', 'file'],
            'propagate': True,
            'level': 'INFO',
        },
        'tock-auth': {
            'handlers': ['console', 'file'],
            'propagate': True,
            'level': 'INFO',
        },
        'tock-employees': {
            'handlers': ['console', 'file'],
            'propagate': True,
            'level': 'INFO',
        },
        'tock-hours': {
            'handlers': ['console', 'file'],
            'propagate': True,
            'level': 'INFO',
        },
        'tock': {
            'handlers': ['console', 'file'],
            'propagate': True,
            'level': 'INFO',
        },
    },
}


try:
    from .local_settings import *     # noqa
except ImportError:
    pass
