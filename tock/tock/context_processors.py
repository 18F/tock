import re
from django.conf import settings


def version_url(request):
    base_url = 'https://github.com/18F/tock/'
    name = settings.VERSION
    response = {
        'x_tock_release_url': '%stree/%s' % (base_url, name),
        'x_tock_release_name': name,
    }

    # Regular expression here matches the regular expression found in
    # .circleci/config.yml for filtering on tags for Production deployments
    if re.match(r'v20[1-9][0-9][0-9]+\.[0-9]+', name):
        response['x_tock_release_url'] = '%sreleases/tag/%s' % (base_url, name)
    elif name != 'main':
        response['x_tock_release_name'] = name[:7]

    return response


def tock_settings_for_context(request):
    """
    Add select values from settings to every context
    """
    return {
        'x_tock_change_request_form_url': settings.TOCK_CHANGE_REQUEST_FORM,
        'x_tock_session_timeout_ms': settings.AUTO_LOGOUT_DELAY_MINUTES * 60000
    }
