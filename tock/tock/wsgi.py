"""
WSGI config for tock project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""
import newrelic
newrelic.initialize()

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tock.settings.production')

from django.core.wsgi import get_wsgi_application
# important that the whitenoise import is after the line above
from whitenoise.django import DjangoWhiteNoise

application = get_wsgi_application()
application = DjangoWhiteNoise(application)
