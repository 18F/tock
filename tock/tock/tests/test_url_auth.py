from django.test import TestCase
from django.core.urlresolvers import RegexURLPattern, RegexURLResolver, reverse

import tock.urls

DOT_STAR_GROUP = '(.+)'

SAMPLE_DOT_STAR_ARG = "foo"

SAMPLE_KWARGS = {
    "reporting_period": "2018-01-01",
    "reporting_period_start_date": "2018-01-02",
    "username": "bar",
    "pk": "1",
    "content_type_id": "2",
    "object_id": "3",
    "app_label": "hours",
}

IGNORE_NAMESPACES = ['djdt']

NAMESPACES_WITH_UNNAMED_PATTERNS = ['admin']


def iter_patterns(urlconf, patterns=None, namespace=None):
    if patterns is None:
        patterns = urlconf.urlpatterns
    for pattern in patterns:
        if isinstance(pattern, RegexURLPattern):
            viewname = pattern.name
            if viewname is None and namespace not in NAMESPACES_WITH_UNNAMED_PATTERNS:
                raise AssertionError(f'namespace {namespace} cannot contain unnamed patterns')
            if namespace and viewname is not None:
                viewname = f"{namespace}:{viewname}"
            yield (viewname, pattern.regex)
        elif isinstance(pattern, RegexURLResolver):
            if pattern.regex.groups > 0:
                raise AssertionError('resolvers are not expected to have groups')
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
    for viewname, regex in iter_patterns(urlconf):
        if viewname is None:
            continue

        named_groups = regex.groupindex.keys()
        kwargs = {}
        args = ()

        if len(named_groups) != regex.groups:
            if regex.groups != 1:
                raise AssertionError('Patterns can contain at most one unnamed group')
            if DOT_STAR_GROUP not in regex.pattern:
                raise AssertionError(f'Unnamed groups can only contain {DOT_STAR_GROUP}')
            args = (SAMPLE_DOT_STAR_ARG,)
        for kwarg in named_groups:
            if kwarg not in SAMPLE_KWARGS:
                raise AssertionError(
                    f'Sample value for {kwarg} in pattern "{regex.pattern}" not found'
                )
            kwargs[kwarg] = SAMPLE_KWARGS[kwarg]
        url = reverse(viewname, urlconf=urlconf, args=args, kwargs=kwargs)
        yield (viewname, url)


class URLAuthTests(TestCase):
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
    ]

    def assertURLIsProtectedByAuth(self, url):
        response = self.client.get(url)
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
                f'GET {url} returned HTTP {code}, but should redirect to login or '
                f'deny access'
            )

    @classmethod
    def define_tests_for_urls(cls, urlconf):
        def create_url_auth_test(url):
            def test(self):
                self.assertURLIsProtectedByAuth(url)
            return test

        for viewname, url in iter_sample_urls(urlconf):
            if url not in cls.IGNORE_URLS:
                setattr(cls, f'test_{viewname}', create_url_auth_test(url))


URLAuthTests.define_tests_for_urls(tock.urls)
