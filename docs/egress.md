# Tock egress filtering

[:arrow_left: Back to Tock Documentation](../docs)

As part of Tock's compliance process, egress filtering is set up for cloud.gov deployments of Tock. Specifically, Tock fulfills the [NIST 800-53 rev5 SC-7 control](https://csrc.nist.gov/Projects/risk-management/sp800-53-controls/release-search#!/control?version=5.1&number=sc-7), which states:

> Connect to external networks or systems only through managed interfaces consisting of boundary protection devices arranged in accordance with an organizational security and privacy architecture.

Accordingly, we have configured [a Caddy proxy](https://github.com/GSA-TTS/cg-egress-proxy) with an [allow list and deny list](../egress_proxy/tock.vars.yml). This proxy configuration rejects all external connections to all sites save for these exceptions:

- `uaa.fr.cloud.gov`: The [cloud.gov UAA server](https://cloud.gov/docs/management/leveraging-authentication/) which in turn uses GSA SecureAuth for authentication.
- `google-analytics.com`: [DAP](https://digital.gov/guides/dap/), for web app analytics
- `api.newrelic.com`: [New Relic endpoints](https://docs.newrelic.com/docs/apis/rest-api-v2/get-started/introduction-new-relic-rest-api-v2/) which is used for the `newrelic-admin` tool

## A note about cloud.gov egress and spaces

cloud.gov allows configuration of [egress traffic controls](https://cloud.gov/docs/management/space-egress/) on a per-space basis _only_. Also, different network security groups are required for the proxy and application. This is why a separate space is required for the proxy.

## Tock staging setup

### Create the egress proxy

To create a new proxy, we largely follow the [cf-egress-proxy README](https://github.com/GSA-TTS/cg-egress-proxy).

As an example, to set up egress for Tock staging:

Create a new cloud.gov space
```bash
cf login -a api.fr.cloud.gov --sso
cf create-space staging-egress -o gsa-18f-tock
```

Clone the egress proxy from [GSA-TTS/cf-egress-proxy](https://github.com/GSA-TTS/cg-egress-proxy). Refer to its documentation for more information about local development.
```bash
git clone git@github.com:GSA-TTS/cg-egress-proxy.git
```

Copy over [vars.tock.yml](../egress_proxy/tock.vars.yml) and configure it for your application. Use `uuidgen` for the username and password. Also copy over the [manifest.yml](../egress_proxy/manifest.yml). Finally, push the egress application to your space.

```bash
cf target -s staging-egress
cf push --vars-file tock.vars.yml
```

SSH into the proxy to make sure that it is running and restricting URLs as advertised.

```bash
cf ssh staging-egress -t -c "/tmp/lifecycle/launcher /home/vcap/app /bin/bash 0"

# from the staging-egress terminal

# test that it is blocking egress appropriately
$ curl https://18f.gsa.gov
> curl: (56) Received HTTP code 403 from proxy after CONNECT

# test that it is allowing egress appropriately
$ curl https://google-analytics.com
> (html response)
```

Once that looks good, you will need to set the proxy environment variable on Tock staging. Use the proxy path from the egress space.

```bash
cf target -s tock-staging

# enable tock staging to talk to the egress server
cf add-network-policy tock-staging staging-egress -s staging-egress

# provide an environment variable with the egress_proxy path
cf set-env tock-staging egress_proxy https://<username>:<password>@<egress-host>.apps.internal:61443

# restage the application so it can use the variable
cf restage tock-staging
```

SSH into the Tock staging space and confirm with `curl` that traffic out is being vetted by staging-egress.

__Note:__ The [../.profile](.profile file) (see the [relevant documentation](https://docs.cloudfoundry.org/devguide/deploy-apps/deploy-app.html#profile)) is configured to export the environmental variables `http_proxy` and `https_proxy` to whatever `egress_proxy` is set to. This allows us to update cloud.gov buildpacks and build the application itself without the proxy active. In other words, the proxy is only active once the application has booted up.

If you need to troubleshoot, you may want to start with the logs:

```bash
cf logs staging-egress --recent
```

## A note on SSL certificates

The Python [certifi](https://pypi.org/project/certifi/) library does _not_ pick up on system-wide certificate authority files automatically. Instead, we have configured manifest files to explicitly set the environment variable `REQUESTS_CA_BUNDLE` so that Python libraries, including `certifi`, will use these certificates. If we do not, then all connections to the proxy are considered untrusted (cloud.gov specific certificates are in `/etc/cf-system-certificates` and replicated to `/etc/ssl/certs/ca-certificates.crt`).
