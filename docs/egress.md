# Tock egress filtering

[:arrow_left: Back to Tock Documentation](../docs)

As part of Tock's compliance process, egress filtering is set up for cloud.gov deployments of Tock. Specifically, Tock fulfills the [NIST 800-53 rev5 SC-7 control](https://csrc.nist.gov/Projects/risk-management/sp800-53-controls/release-search#!/control?version=5.1&number=sc-7), which states:

> Connect to external networks or systems only through managed interfaces consisting of boundary protection devices arranged in accordance with an organizational security and privacy architecture.

Accordingly, we have configured [a Caddy proxy](https://github.com/GSA-TTS/cg-egress-proxy) with the following rules:

```
proxydeny:
proxyallow: |
  uaa.fr.cloud.gov
  google-analytics.com
```

That is, this proxy rejects all external connections to all sites save for these two exceptions:

- `uaa.fr.cloud.gov`: The [cloud.gov UAA server](https://cloud.gov/docs/management/leveraging-authentication/) which in turn uses GSA SecureAuth for authentication.
- `google-analytics.com`: [DAP](https://digital.gov/guides/dap/), for web app analytics

## A note about cloud.gov egress and spaces

cloud.gov allows configuration of [egress traffic controls](https://cloud.gov/docs/management/space-egress/) on a per-space basis _only_. Also, different network security groups are required for the proxy and application. This is why a separate space is required for the proxy.

## Tock staging setup

To create a new proxy, follow the [cf-egress-proxy README](https://github.com/GSA-TTS/cg-egress-proxy).

As an example, to set up egress for Tock staging:

- create a new cloud.gov space
  - `cf create-space staging-egress -o gsa-18f-tock`
- git clone [GSA-TTS/cf-egress-proxy](https://github.com/GSA-TTS/cg-egress-proxy)
- build the Caddy proxy (optional, not needed anymore)
  - `make caddy-v2-with-forwardproxy`
  - note: requires Docker
- rename `vars.myapp.yml` to `vars.tock.yml`
  - configure `proxyname`, `hostname`, `username` and `password`
  - configure with above proxy rules
- `cf target -s staging-egress`
- `cf push --vars-file vars.tock.yml`
- enable Tock staging to connect to Tock egress
  - `cf add-network-policy tock-staging staging-egress -s staging-egress`

At this stage it is prudent to verify that the proxy is working as advertised. One way is to `cf ssh` the staging environment (`cf ssh staging-egress -t -c "/tmp/lifecycle/launcher /home/vcap/app /bin/bash 0"`) and test with commands such as `curl -x "https://<username>:<password>@<egress-host>.apps.internal:61443" restricted-domain.com` and make sure Caddy returns a `403 Forbidden`. Similarly, you want to test for trusted domains and verify that the proxy passes these requests through. 

Test that curl connects properly from your application's container.

```bash
# Get a shell inside the app
$ cf ssh staging-egress -t -c "/tmp/lifecycle/launcher /home/vcap/app /bin/bash 0"

# Use curl to test that the container can reach things it should
$ curl http://allowedhost:allowedport
[...response from allowedhost...] # allowed

$ curl https://allowedhost:allowedport
[...response from allowedhost...] # allowed

# Use curl to test that the container can't reach things it shouldn't
$ curl http://allowedhost:deniedport
curl: (56) Received HTTP code 403 from proxy after CONNECT # denied

$ curl http://deniedhost:allowedport
curl: (56) Received HTTP code 403 from proxy after CONNECT # denied

$ curl https://allowedhost:deniedport
curl: (56) Received HTTP code 403 from proxy after CONNECT # denied

$ curl https://deniedhost:allowedport
curl: (56) Received HTTP code 403 from proxy after CONNECT # denied
```

Once everything looks good:

- set the proxy environment variable on Tock staging
  - `cf set-env tock-staging egress_proxy https://<username>:<password>@<egress-host>.apps.internal:61443`
- restage Tock staging
  - `cf restage tock-staging`
    - Note that the [../.profile](.profile file) (see the [relevant documentation](https://docs.cloudfoundry.org/devguide/deploy-apps/deploy-app.html#profile)) is configured to export the environmental variables `http_proxy` and `https_proxy` to whatever `egress_proxy` is set to.
    - Doing so allows us to update cloud.gov buildpacks and build the application itself without the proxy active. In other words, the proxy is only active once the application has booted up.

## A note on SSL certificates

The Python [certifi](https://pypi.org/project/certifi/) library does _not_ pick up on system-wide certificate authority files automatically. Instead, we have configured manifest files to explicitly set the environment variable `REQUESTS_CA_BUNDLE` so that Python libraries, including `certifi`, will use these certificates. If we do not, then all connections to the proxy are considered untrusted (cloud.gov specific certificates are in `/etc/cf-system-certificates` and replicated to `/etc/ssl/certs/ca-certificates.crt`).
