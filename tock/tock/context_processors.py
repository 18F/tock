import re
from django.conf import settings
from employees.models import UserData


def version_url(request):
    base_url = 'https://github.com/18F/tock/'
    name = settings.VERSION
    response = {
        'x_tock_release_url': '%stree/%s' % (base_url, name),
        'x_tock_release_name': name,
    }

    # Regular expression here matches the regular expression found in
    # .circleci/config.yml for filtering on tags for Production deployments
    if re.match('v20[1-9][0-9][0-9]+\.[0-9]+', name):
        response['x_tock_release_url'] = '%sreleases/tag/%s' % (base_url, name)
    elif name != 'master':
        response['x_tock_release_name'] = name[:7]

    return response

def tock_request_form_url(request):
    return {
        'x_tock_change_request_form_url': settings.TOCK_CHANGE_REQUEST_FORM,
    }

def user_attendance(request):
    response = {
        'x_tock_user_is_late': None
    }

    try:
        udata = UserData.objects.get(user=request.user)
        response['x_tock_user_is_late'] = udata.is_late()
    except UserData.DoesNotExist:
        response['x_tock_user_is_late'] = False

    return response
