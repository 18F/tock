from __future__ import absolute_import

import newrelic.agent
from cfenv import AppEnv

env = AppEnv()


def initialize():
    settings = newrelic.agent.global_settings()
    settings.app_name = env.get_credential('NEW_RELIC_APP_NAME')
    settings.license_key = env.get_credential('NEW_RELIC_LICENSE_KEY')
    if settings.app_name and settings.license_key:
        newrelic.agent.initialize()