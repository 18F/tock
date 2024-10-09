# Tock egress filtering

[:arrow_left: Back to Tock Documentation](../docs)

As part of Tock's compliance process, egress filtering is set up for cloud.gov deployments of Tock. Specifically, Tock fulfills the [NIST 800-53 rev5 SC-7 control](https://csrc.nist.gov/Projects/risk-management/sp800-53-controls/release-search#!/control?version=5.1&number=sc-7), which states:

> Connect to external networks or systems only through managed interfaces consisting of boundary protection devices arranged in accordance with an organizational security and privacy architecture.

Accordingly, we have configured [a Caddy proxy](https://github.com/GSA-TTS/cg-egress-proxy) with an [allow list and deny list](../egress_proxy/tock.vars.yml). This proxy configuration rejects all external connections to all sites save for these exceptions:

- `uaa.fr.cloud.gov`: The [cloud.gov UAA server](https://cloud.gov/docs/management/leveraging-authentication/) which in turn uses GSA SecureAuth for authentication.
- `google-analytics.com`: [DAP](https://digital.gov/guides/dap/), for web app analytics
- `api.newrelic.com`: The [New Relic REST API endpoint](https://docs.newrelic.com/docs/apis/rest-api-v2/get-started/introduction-new-relic-rest-api-v2/) which is used by the `newrelic-admin` tool to record deployments
- `gov-collector.newrelic.com`: The FedRAMP-compliant [New Relic APM collector endpoint](https://docs.newrelic.com/docs/security/security-privacy/compliance/fedramp-compliant-endpoints/#agents), used by the New Relic Python agent

## A note about cloud.gov egress and spaces

cloud.gov allows configuration of [egress traffic controls](https://cloud.gov/docs/management/space-egress/) on a per-space basis _only_. Also, different network security groups are required for the proxy and application. This is why a separate space is required for the proxy.

## Tock staging setup

Updating Tock's egress proxy settings is a rarely performed, highly manual process that requires rebuilding the proxy configuration in a local development environment. If possible, seek an administrator of this repo to pair with you as you make changes.

The following instructions use the staging egress proxy as an example.

### Clone the proxy application repo

Pull the current version of the Caddy proxy application from [GSA-TTS/cf-egress-proxy](https://github.com/GSA-TTS/cg-egress-proxy). Refer to its documentation for more information about local development.

#### First-time setup

If you have not previously cloned the repo, do so:
```bash
git clone git@github.com:GSA-TTS/cg-egress-proxy.git
```

#### Updating an existing repo

If you have previously cloned the repo, ensure you are working from the current version with git:

1. Stash or delete any local changes
2. Check out the `main` branch
3. Pull the `main` branch from upstream

### Log in with the Cloud Foundry CLI tool

```bash
cf login -a api.fr.cloud.gov --sso
```

### Create a new egress proxy (if needed)

If you are setting up a new egress proxy from scratch, create a new cloud.gov space:
```bash
cf create-space staging-egress -o gsa-18f-tock
```

### Target the staging-egress CF space

```bash
cf target -s staging-egress
```

### Configure the `tock.vars.yml` file for the proxy

Copy these files from from your local `tock` repo into your `cf-egress-proxy` repo:

1. [tock.vars.yml](../egress_proxy/tock.vars.yml)
2. [manifest.yml](../egress_proxy/manifest.yml)

#### Set username and password

In your `cf-egress-proxy` repo, manually set the `username` and `password` values in `tock.vars.yml`.

##### When creating a new proxy

Use the `uuidgen` command to create a new, random username and password. Paste each into the vars file for the appropriate key.

##### When updating an existing proxy

Retrieve the existing proxy username and password from the deployed egress proxy application:

```bash
cf env staging-egress | grep PROXY_USERNAME
```

Paste each value into the vars file for the appropriate key.

#### Deploy the egress proxy application

Push the egress proxy application to your space.

```bash
cf target -s staging-egress
cf push --vars-file tock.vars.yml
```

### Validate the proxy

SSH into the proxy application's container to make sure that it is running and restricting URLs as advertised.

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

### Configure Tock application to use the egress proxy

Once the egress proxy looks good, you will need to set the proxy environment variable on Tock staging.
Use the proxy path from the egress space.

```bash
cf target -s tock-staging

# enable tock staging to talk to the egress server
cf add-network-policy tock-staging staging-egress -s staging-egress --protocol tcp --port 61443

# set an environment variable with the egress_proxy path
cf set-env tock-staging egress_proxy https://<username>:<password>@<egress-host>.apps.internal:61443

# restage the application so it can use the variable
cf restage tock-staging
```

### Validate Tock configuration

SSH into the Tock staging space and confirm with `curl` that traffic out is being vetted by staging-egress.

```bash
cf ssh tock-staging -t -c "/tmp/lifecycle/launcher /home/vcap/app /bin/bash 0"

# from the tock-staging terminal

# test that it is blocking egress appropriately
$ curl https://18f.gsa.gov
> curl: (56) Received HTTP code 403 from proxy after CONNECT

# test that it is allowing egress appropriately
$ curl https://google-analytics.com
> (html response)
```

### Troubleshooting

To troubleshoot end-to-end traffic, you may want to start with the egress proxy logs:

```bash
cf logs staging-egress --recent
```

If network calls from the Tock application are reaching the egress proxy, you should see log lines from the proxy indicating whether the calls were allowed or denied.

If a call from the Tock application is behaving unexpectedly (i.e. failing when it should be allowed, or succeeding when it should be denied):

* If the proxy logs show that the proxy is processing the call, double-check the `proxyallow` and `proxydeny` settings in [tock.vars.yml](../egress_proxy/tock.vars.yml).
* If the proxy log doesn't contain any record of the call, double-check the URL in the `egress_proxy` environment variable and the network policy for the Tock application.

## A note on proxy URL environment variables

The [.profile file](../.profile) (see the [relevant documentation](https://docs.cloudfoundry.org/devguide/deploy-apps/deploy-app.html#profile)) is configured to export the environmental variables `http_proxy` and `https_proxy` to whatever `egress_proxy` is set to. This allows us to update cloud.gov buildpacks and build the application itself without the proxy active. In other words, the proxy is only active once the application has booted up.

It additionally exports a `NEW_RELIC_PROXY_HOST` variable set to the value of `egress_proxy`. This variable is required by the New Relic Python agent and `newrelic-admin` tool.

## A note on SSL certificates

The Python [certifi](https://pypi.org/project/certifi/) library does _not_ pick up on system-wide certificate authority files automatically. Instead, we have configured manifest files to explicitly set the environment variable `REQUESTS_CA_BUNDLE` so that Python libraries, including `certifi`, will use these certificates. If we do not, then all connections to the proxy are considered untrusted (cloud.gov specific certificates are in `/etc/cf-system-certificates` and replicated to `/etc/ssl/certs/ca-certificates.crt`).
