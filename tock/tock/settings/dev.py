import os
import sys
import dj_database_url

from .base import *  # noqa
# spell out explicit variable dependencies
from .base import (DATABASES, INSTALLED_APPS, MIDDLEWARE, TEMPLATES)

DEBUG = True

SECRET_KEY = 'development_mode'  # nosec

for t in TEMPLATES:
    t.setdefault('OPTIONS', {})
    t['OPTIONS']['debug'] = True

DEBUG_TOOLBAR_PATCH_SETTINGS = False

INTERNAL_IPS = [
    '127.0.0.1',
    '::1',
]

DATABASES['default'] = dj_database_url.config(
    default='postgres://tock:tock@localhost/tock'
)

INSTALLED_APPS += ('nplusone.ext.django', )
MIDDLEWARE += ('nplusone.ext.django.NPlusOneMiddleware', )

# Change this setting to True in order to discover potentially inefficient
# queries while doing active development using nplusone.
NPLUSONE_RAISE = False

IS_RUNNING_TEST_SUITE = (os.path.basename(sys.argv[0]) == 'manage.py'
                         and len(sys.argv) > 1 and sys.argv[1] == 'test')

if not IS_RUNNING_TEST_SUITE:
    INSTALLED_APPS += ('debug_toolbar', )
    MIDDLEWARE += ('debug_toolbar.middleware.DebugToolbarMiddleware', )
else:
    NPLUSONE_RAISE = True

MEDIA_ROOT = './media/'
MEDIA_URL = '/media/'

# Due to the Docker configuration, bypass Django Debug Toolbar's check
# on INTERAL_IPS to display itself, opt to show the debug toolbar with
# a custom callback instead.
# https://django-debug-toolbar.readthedocs.io/en/1.9.1/configuration.html#toolbar-options (SHOW_TOOLBAR_CALLBACK)
def show_django_debug_toolbar(request):
    return DEBUG

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': 'tock.settings.dev.show_django_debug_toolbar',
}

USE_X_FORWARDED_HOST = True

try:
  from .local_settings import *     # noqa
except ImportError:
  pass

UAA_CLIENT_ID = 'testtesttesttesttesttesttesttesttesttesttest'
UAA_CLIENT_SECRET = 'testtesttesttesttesttesttesttesttesttest' # nosec
UAA_AUTH_URL = 'fake:'
UAA_TOKEN_URL = 'fake:' # nosec
