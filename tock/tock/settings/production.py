import os

from .base import *


SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '')
ALLOWED_HOSTS = ['*']  # proxied

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get('PG_NAME', ''),
        "USER": os.environ.get('PG_USER', ''),
        "PASSWORD": os.environ.get('PG_PASS', ''),
        "HOST": os.environ.get('PG_HOST', ''),
    },
}

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

try:
    from .local_settings import *
except ImportError:
    pass
