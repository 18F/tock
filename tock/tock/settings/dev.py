from .base import *  # noqa
import os

DEBUG = True
TEMPLATE_DEBUG = True

INTERNAL_IPS = ('127.0.0.1',)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'tock',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'tock',
        'PASSWORD': 'tock',
        'HOST': os.environ.get('DATABASE_HOST'),
        'PORT': '',                      # Set to empty string for default.
    }
}

INSTALLED_APPS += ('debug_toolbar',)

DEBUG_TOOLBAR_PATCH_SETTINGS = False

MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

INTERNAL_IPS = ['127.0.0.1', '::1', '192.168.33.10']

MEDIA_ROOT = './media/'
MEDIA_URL = '/media/'

try:
  from .local_settings import *
except ImportError:
  pass
