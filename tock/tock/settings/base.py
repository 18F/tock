"""
Django settings for tock.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

from django.utils.crypto import get_random_string

from .env import env

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATABASES = {}
ROOT_URLCONF = 'tock.urls'
WSGI_APPLICATION = 'tock.wsgi.application'
SECRET_KEY = env.get_credential('DJANGO_SECRET_KEY', get_random_string(50))
LOGIN_URL = '/auth/login'
LOGIN_REDIRECT_URL = '/'

CSRF_FAILURE_VIEW = 'tock.views.csrf_failure'

INSTALLED_APPS = (
    'django.contrib.contenttypes',  # may be okay to remove
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'uaa_client',
    'tock',
    'projects',
    'hours',
    'employees',
    'organizations',
    'api',
    'utilization',
    'rest_framework.authtoken',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            '/templates/'
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
                'tock.context_processors.version_url',
            ],
        },
    },
]


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'uaa_client.middleware.UaaRefreshMiddleware',
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
        'rest_framework.authentication.SessionAuthentication',
    ),
}

VERSION = env.get_credential('CIRCLE_TAG', 'master')

UAA_APPROVED_DOMAINS = {
    'gsa.gov',
}
UAA_CLIENT_ID = env.get_credential('UAA_CLIENT_ID', None)
UAA_CLIENT_SECRET = env.get_credential('UAA_CLIENT_SECRET', None)
UAA_AUTH_URL = 'https://login.fr.cloud.gov/oauth/authorize'
UAA_TOKEN_URL = 'https://uaa.fr.cloud.gov/oauth/token'
