# Creating UAA Clients for Tock

[:arrow_left: Back to Tock Documentation](README.md)

Tock leverages [UAA authentication provided by cloud.gov][cg-uaa-auth] to
authenticate users. This document talks about how to create and rotate these UAA
clients using the [cf-cli][].


[cf-cli]: https://cloudfoundry.org/


Steps:

- Creating the UAA client
  - Setting the redirect URI
- Updating the user-provided service for Tock

## Creating a UAA client

Go read the [cloud.gov identity provider documentation][cg-uaa-auth] to learn
about creating the oAuth client. The Tock application only requires the `openid`
scope for the oAuth client.

Tock uses the following naming convention for oAuth clients Service Instances
and Service Keys.

<details>
<summary>Production oAuth client Service Name Example</summary>

```shell
${APP_NAME}-${SERVICE_PLAN_NAME}
```

For instance, the Production oAuth client Service is called `tock-oauth-client`.

</details>

<br>

<details>
<summary>Production oAuth client Service Key Example</summary>

```shell
${APP_NAME}-${SERVICE_PLAN_NAME}-${YEARMONTHDAY}
```

For instance, the Production oAuth client Service Key is called `tock-oauth-client-20180307` because it was created on March 7th, 2018.

</details>

[cg-uaa-auth]: https://cloud.gov/docs/services/cloud-gov-identity-provider/

### Setting the Redirect URI

The redirect URI for Tock is whatever the URL is for the application with a path
of `/auth/callback`

<details>
<summary>Production Redirect URI Example</summary>

```shell
# ...
 -c '{"redirect_uri": ["https://tock.18f.gov/auth/callback"]}'
```

Keep in mind that if you're deploying multiple Tock applications with different
URLs, you can add multiple `redirect_uri` URLs that end in `/auth/callback`.

</details>
