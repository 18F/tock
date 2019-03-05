from django.test import TestCase
from django.urls import reverse, URLPattern
from django.urls.resolvers import URLResolver

import tock.urls

# Some URLconf patterns contain unnamed capture groups.
# These constants just tell us what they look like, and what sample
# values to use when we want to generate a sample URL for them.
DOT_STAR_GROUP = '(.+)'
SAMPLE_DOT_STAR_ARG = "foo"

# When a URLconf pattern contains named capture groups, we'll use this
# dictionary to retrieve a sample value for it, which will be included
# in the sample URLs we generate, when attempting to perform a GET
# request on the view.
SAMPLE_KWARGS = {
    "reporting_period": "2018-01-01",
    "reporting_period_start_date": "2018-01-02",
    "username": "bar",
    "pk": "1",
    "id": "1",
    "content_type_id": "2",
    "object_id": "3",
    "app_label": "hours",
}

# Our test suite will ignore some namespaces.
IGNORE_NAMESPACES = [
    # The Django Debug Toolbar (DJDT) ends up in the URL config but it's always
    # disabled in production, so don't worry about it.
    'djdt'
]

# In general, we don't want to have any unnamed views, because that makes it
# impossible to generate sample URLs that point at them. We'll make exceptions
# for some namespaces that we don't have control over, though.
NAMESPACES_WITH_UNNAMED_VIEWS = [
    'admin'
]


def iter_patterns(urlconf, patterns=None, namespace=None):
    """
    Iterate through all patterns in the given Django URLconf.  Yields
    `(viewname, route)` tuples, where `viewname` is the fully-qualified view name
    (including its namespace, if any), and `route` is a regular expression that
    corresponds to the part of the pattern that contains any capturing groups.
    """
    if patterns is None:
        patterns = urlconf.urlpatterns
    for pattern in patterns:
        # Resolve if it's a route or an include
        if isinstance(pattern, URLPattern):
            viewname = pattern.name
            if viewname is None and namespace not in NAMESPACES_WITH_UNNAMED_VIEWS:
                raise AssertionError(f'namespace {namespace} cannot contain unnamed views')
            if namespace and viewname is not None:
                viewname = f"{namespace}:{viewname}"
            yield (viewname, pattern.pattern)
        elif isinstance(pattern, URLResolver):
            if len(pattern.default_kwargs.keys()) > 0:
                raise AssertionError('resolvers are not expected to have kwargs')
            if pattern.namespace and namespace is not None:
                raise AssertionError('nested namespaces are not currently supported')
            if pattern.namespace in IGNORE_NAMESPACES:
                continue
            yield from iter_patterns(
                urlconf,
                pattern.url_patterns,
                namespace or pattern.namespace
            )
        else:
            raise AssertionError('unknown pattern class')


def iter_sample_urls(urlconf):
    """
    Yields sample URLs for all entries in the given Django URLconf.
    This gets pretty deep into the muck of RoutePattern
    https://docs.djangoproject.com/en/2.1/_modules/django/urls/resolvers/
    """

    for viewname, route in iter_patterns(urlconf):
        if not viewname:
            continue
        if viewname == 'auth_user_password_change':
            print(route)
            break
        named_groups = route.regex.groupindex.keys()
        kwargs = {}
        args = ()

        for kwarg in named_groups:
            if kwarg not in SAMPLE_KWARGS:
                raise AssertionError(
                    f'Sample value for {kwarg} in pattern "{route}" not found'
                )
            kwargs[kwarg] = SAMPLE_KWARGS[kwarg]

        url = reverse(viewname, args=args, kwargs=kwargs)
        yield (viewname, url)


class URLAuthTests(TestCase):
    """
    Tests to ensure that most URLs in a Django URLconf are protected by
    authentication.
    """

    # We won't test that the following URLs are protected by auth.
    # Note that the trailing slash is wobbly depending on how the URL was defined.
    IGNORE_URLS = [
        # These are the UAA auth endpoints that always need
        # to be public.
        '/auth/login',
        '/auth/callback',
        # These end up in the URL config but are always
        # disabled in production, so don't worry about them.
        '/auth/fake/oauth/authorize',
        '/auth/fake/oauth/token',
        # Logging out of admin is always public, so ignore it.
        '/admin/logout/',
        # And logging out of the site is always public too.
        '/logout',
    ]

    def assertURLIsProtectedByAuth(self, url):
        """
        Make a GET request to the given URL, and ensure that it either redirects
        to login or denies access outright.
        """

        try:
            response = self.client.get(url)
        except Exception as e:
            # It'll be helpful to provide information on what URL was being
            # accessed at the time the exception occurred.  Python 3 will
            # also include a full traceback of the original exception, so
            # we don't need to worry about hiding the original cause.
            raise AssertionError(f'Accessing {url} raised "{e}"', e)

        code = response.status_code
        if code == 302:
            redirect = response['location']
            self.assertRegex(
                redirect,
                r'^\/(auth|admin)\/login',
                f'GET {url} should redirect to login or deny access, but instead '
                f'it redirects to {redirect}'
            )
        elif code == 401 or code == 403:
            pass
        else:
            raise AssertionError(
                f'GET {url} returned HTTP {code}, but should redirect to login or deny access',
            )

    @classmethod
    def define_tests_for_urls(cls, urlconf):
        """
        This class method dynamically adds test methods to the class which
        test the security properties of individual URLs in a URLconf.  It's a hack,
        because Python's built-in unittest package doesn't provide any
        means for parameterizing tests.
        """

        def create_url_auth_test(url):
            def test(self):
                self.assertURLIsProtectedByAuth(url)
            return test

        for viewname, url in iter_sample_urls(urlconf):
            if url not in cls.IGNORE_URLS:
                setattr(cls, f'test_{viewname}', create_url_auth_test(url))


URLAuthTests.define_tests_for_urls(tock.urls)
