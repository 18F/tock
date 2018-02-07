def version_url(request):
    import re
    from django.conf import settings
    base_url = 'https://github.com/18F/tock/'
    name = settings.VERSION
    response = {
        'release_url': '%stree/%s' % (base_url, name),
        'release_name': settings.VERSION,
    }
    if re.match('/v20[1-9][0-9][0-9]+\.[0-9]+/', name):
        response['release_url'] = '%sreleases/tag/%s' % (base_url, name)

    return response
