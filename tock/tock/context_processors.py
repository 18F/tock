import re
from django.conf import settings


def version_url(request):
    base_url = 'https://github.com/18F/tock/'
    name = settings.VERSION
    response = {
        'x_tock_release_url': '%stree/%s' % (base_url, name),
        'x_tock_release_name': name,
    }
    if re.match('/v20[1-9][0-9][0-9]+\.[0-9]+/', name):
        response['release_url'] = '%sreleases/tag/%s' % (base_url, name)

    return response
