"""
Django settings for tock.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


DATABASES = {}
# ALLOWED_HOSTS = []
# Application definition

INSTALLED_APPS = (
    'django.contrib.contenttypes',  # may be okay to remove
    'django.contrib.staticfiles',
    'social.apps.django_app.default',
    'tock',
    'projects',
    'hours'
)

ROOT_URLCONF = 'tock.urls'
WSGI_APPLICATION = 'tock.wsgi.application'

# Default + request
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
)

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_ROOT = '/var/www/static/'

TEMPLATE_DIRS = (
    '/templates/',
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATIC_URL = '/static/'

USE_TZ = True
TIME_ZONE = 'UTC'

# Django Social Auth Config
 
AUTHENTICATION_BACKENDS = ( 
    'social.backends.google.GoogleOAuth2',  # putting this 1st means that most users will auth with their Google identity
    'django.contrib.auth.backends.ModelBackend',        # ...but this one means we can still have local admin accounts as a fallback
)
LOGIN_URL = '/login/google-oauth2/'
LOGIN_REDIRECT_URL = '/'
 
SOCIAL_AUTH_RAISE_EXCEPTIONS = False
SOCIAL_AUTH_PROCESS_EXCEPTIONS = 'social_auth.utils.log_exceptions_to_messages'  # ...assuming you like the messages framework
 
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY      = os.environ.get('GOOGLE_OAUTH2_CLIENT_ID')  # this is on the credentials web page from above
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET  = os.environ.get('GOOGLE_OAUTH2_CLIENT_SECRET')    # this is also on the credentials web page from above
GOOGLE_WHITE_LISTED_DOMAINS = os.environ.get('GOOGLE_WHITE_LISTED_DOMAINS')  # this is what actually limits access
 
SOCIAL_AUTH_COMPLETE_URL_NAME  = 'socialauth_complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'socialauth_associate_complete'