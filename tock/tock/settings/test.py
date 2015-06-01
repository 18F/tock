from .base import *

from django.utils.crypto import get_random_string

SECRET_KEY = get_random_string(50)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

MEDIA_ROOT = './media/'
