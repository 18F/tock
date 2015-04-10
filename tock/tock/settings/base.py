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

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATABASES = {}
# ALLOWED_HOSTS = []
# Application definition

INSTALLED_APPS = ('django.contrib.contenttypes',  # may be okay to remove
                  'django.contrib.staticfiles', 'django.contrib.admin',
                  'django.contrib.auth', 'django.contrib.sessions',
                  'django.contrib.messages', 'tock', 'projects', 'hours')

ROOT_URLCONF = 'tock.urls'
WSGI_APPLICATION = 'tock.wsgi.application'

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', get_random_string(50))

# Default + request
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static", "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request")

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'tock.remote_user_auth.EmailHeaderMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',)

AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.RemoteUserBackend',)

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

TEMPLATE_DIRS = ('/templates/',)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = '/tock/static/'

AUTH_USER_MODEL = 'auth.User'
