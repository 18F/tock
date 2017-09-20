"""
Django settings for tock.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import json

from django.utils.crypto import get_random_string

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATABASES = {}
ROOT_URLCONF = 'tock.urls'
WSGI_APPLICATION = 'tock.wsgi.application'
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', get_random_string(50))

# Float (external workforce scheduling service) variables.
# See README.md for description.
def get_cups_key(keyname):
    if os.environ.get('VCAP_SERVICES'):
        key = str(json.loads(os.environ.get(
            'VCAP_SERVICES'))['user-provided'][0]['credentials'][keyname])
        return key
    else:
        return ''
FLOAT_API_KEY = get_cups_key('float-key')
FLOAT_API_URL_BASE = 'https://api.float.com/api/v1'
FLOAT_API_HEADER = {'Authorization': 'Bearer ' + FLOAT_API_KEY}

INSTALLED_APPS = (
    'django.contrib.contenttypes',  # may be okay to remove
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'tock',
    'projects',
    'hours',
    'employees',
    'api',
    'utilization',
    'rest_framework.authtoken',
)

TEMPLATES =  [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['/templates/'
            ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'tock.remote_user_auth.EmailHeaderMiddleware',
    'tock.remote_user_auth.UserDataMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'tock.remote_user_auth.TockUserBackend',
)

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'US/Eastern'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

ALLOWED_EMAIL_DOMAINS = {
    'gsa.gov',
}

REST_FRAMEWORK = {
    'UNICODE_JSON': False,
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        # use our CSV renderer instead of rest_framework_csv's
        'api.renderers.PaginatedCSVRenderer',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
}
