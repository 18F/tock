import dj_database_url

from .base import *  # noqa

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEBUG_TOOLBAR_PATCH_SETTINGS = False

DATABASES['default'] = dj_database_url.config(
    default='postgres://tock:tock@localhost/tock'
)

INSTALLED_APPS += (
    'debug_toolbar',
)

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INTERNAL_IPS = [
    '127.0.0.1',
    '::1',
    '192.168.33.10',
]

MEDIA_ROOT = './media/'
MEDIA_URL = '/media/'

try:
  from .local_settings import *
except ImportError:
  pass
