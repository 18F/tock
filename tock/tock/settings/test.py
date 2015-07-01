from .base import *  # noqa

from django.utils.crypto import get_random_string

SECRET_KEY = get_random_string(50)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

INSTALLED_APPS += ('django_nose', )
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=tock,employees,projects,hours,api',
]

MEDIA_ROOT = './media/'
