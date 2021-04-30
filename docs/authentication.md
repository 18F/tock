## Tock authentication

[:arrow_left: Back to Tock Documentation](../docs)

18F's current deployment of Tock relies on
[cloud.gov's User Account and Authentication (UAA) server][UAA] for
authentication.

During development, a ["fake" cloud.gov UAA server][fakeUAA] is used for
authentication. Here, you can enter any email address. If the
address is `@gsa.gov`, then a non-staff account will automatically
be created for that user. They'll be logged in, but otherwise their access
will be denied.

The easiest way to create an administrative user is to follow the instructions
in [Getting Started with Local Tock
Development](local-development.md#getting-started-with-local-tock-development).

[UAA]: https://cloud.gov/docs/management/leveraging-authentication/
[fakeUAA]: http://cg-django-uaa.readthedocs.io/en/latest/quickstart.html#using-the-fake-cloud-gov-server

### Creating UAA clients for Tock

Tock leverages [UAA authentication provided by cloud.gov][cg-uaa-auth] to
authenticate users. This document talks about how to create and rotate these UAA
clients using the [cf-cli][]. The following documentation assumes you are
[comfortable using the cf-cli][cf-cli-docs].

[cf-cli]: https://github.com/cloudfoundry/cli
[cf-cli-docs]: https://docs.cloudfoundry.org/cf-cli/install-go-cli.html

#### Creating a UAA client

We encourage you to read the [cloud.gov identity provider documentation][cg-uaa-auth] to learn
about creating the oAuth client. The Tock application only requires the `openid`
scope for the oAuth client.

Tock uses the following naming convention for oAuth clients' Service Instances
and Service Keys:

##### Production oAuth client Service Name example

```shell
${APP_NAME}-${SERVICE_PLAN_NAME}
```

For instance, the Production oAuth client Service is called `tock-oauth-client`.

##### Production oAuth client Service Key example

```shell
${APP_NAME}-${SERVICE_PLAN_NAME}-${YEARMONTHDAY}
```

For instance, the Production oAuth client Service Key is called
`tock-oauth-client-20180307` because it was created on March 7th, 2018.

[cg-uaa-auth]: https://cloud.gov/docs/services/cloud-gov-identity-provider/

#### Setting the redirect URI

The redirect URI for Tock is whatever the URL is for the application with a path
of `/auth/callback`.

##### Production redirect URI example

```shell
# ...
 -c '{"redirect_uri": ["https://tock.18f.gov/auth/callback"]}'
```

Keep in mind that if you're deploying multiple Tock applications with different
URLs, you can add multiple `redirect_uri` URLs that end in `/auth/callback`.
