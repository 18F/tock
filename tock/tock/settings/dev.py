import os
import sys
import dj_database_url

from .base import *  # noqa

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEBUG_TOOLBAR_PATCH_SETTINGS = False

INTERNAL_IPS = [
    '127.0.0.1',
    '::1',
]

DATABASES['default'] = dj_database_url.config(
    default='postgres://tock:tock@localhost/tock'
)

INSTALLED_APPS += ('nplusone.ext.django', )
MIDDLEWARE_CLASSES += ('nplusone.ext.django.NPlusOneMiddleware', )

# Change this setting to True in order to discover potentially inefficient
# queries while doing active development using nplusone.
NPLUSONE_RAISE = False

IS_RUNNING_TEST_SUITE = (os.path.basename(sys.argv[0]) == 'manage.py' and
                         len(sys.argv) > 1 and sys.argv[1] == 'test')

if not IS_RUNNING_TEST_SUITE:
    INSTALLED_APPS += ('debug_toolbar', )
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware', )
else:
    NPLUSONE_RAISE = True

MEDIA_ROOT = './media/'
MEDIA_URL = '/media/'

# Due to the Docker configuration and Django Debug Toolbar's need to account
# for the local machine's IP address in INTERNAL_IPS to display itself, opt
# to show the debug toolbar with a custom callback instead. For more
# information on this setup please take a look at these resources:
# https://django-debug-toolbar.readthedocs.io/en/1.4/installation.html#internal-ips
# https://django-debug-toolbar.readthedocs.io/en/1.4/configuration.html#toolbar-options (SHOW_TOOLBAR_CALLBACK)
# http://stackoverflow.com/questions/10517765/django-debug-toolbar-not-showing-up
# https://gist.github.com/douglasmiranda/9de51aaba14543851ca3 (code taken from here)
def show_django_debug_toolbar(request):
    if request.is_ajax():
        return False

    return True

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': 'tock.settings.dev.show_django_debug_toolbar',
}

USE_X_FORWARDED_HOST = True

try:
  from .local_settings import *
except ImportError:
  pass
