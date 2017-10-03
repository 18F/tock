"""
WSGI config for tock project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os

from tock.settings.env import env

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tock.settings.production')

def initialize_newrelic():
    license_key = env.get_credential('NEW_RELIC_LICENSE_KEY')

    if license_key:
        import newrelic.agent
        settings = newrelic.agent.global_settings()
        settings.license_key = license_key
        newrelic.agent.initialize()

initialize_newrelic()

from django.core.wsgi import get_wsgi_application
# important that the whitenoise import is after the line above
from whitenoise.django import DjangoWhiteNoise

application = get_wsgi_application()
application = DjangoWhiteNoise(application)
