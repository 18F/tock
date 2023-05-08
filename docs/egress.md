# Tock egress filtering

As part of Tock's compliance process, egress filtering is set up for cloud.gov deployments of Tock. Specifically, Tock fulfills the [NIST 800-53 rev5 SC-7 control](https://csrc.nist.gov/Projects/risk-management/sp800-53-controls/release-search#!/control?version=5.1&number=sc-7), which states:

> Connect to external networks or systems only through managed interfaces consisting of boundary protection devices arranged in accordance with an organizational security and privacy architecture.

Accordingly, we have configured [a Caddy proxy](https://github.com/GSA-TTS/cg-egress-proxy) with the following rules:

```
proxydeny:
proxyallow: |
  uaa.fr.cloud.gov
  google-analytics.com
  pypi.python.org
  pypi.org
```

That is, this proxy rejects all external connections to all sites save for these four exceptions:

- `uaa.fr.cloud.gov`: The [cloud.gov UAA server](https://cloud.gov/docs/management/leveraging-authentication/) which in turn uses GSA SecureAuth for authentication.
- `google-analytics.com`: [DAP])(https://digital.gov/guides/dap/)
- `pypi.org`: [Python package repository](https://pypi.org/)
- `pypi.python.org`: Same as above

Note: Tock does not currently vendor Python dependencies.

## A note about cloud.gov egress and spaces

cloud.gov allows configuration of [egress traffic controls](https://cloud.gov/docs/management/space-egress/) only on a per-space basis. Also, different network security groups are required for the proxy and application. This is why a separate space is required for the proxy. 

## Tock staging setup

To create a new proxy, follow the [cf-egress-proxy README](https://github.com/GSA-TTS/cg-egress-proxy).

As an example, to set up egress for Tock staging, the steps were, roughly:

- create a new cloud.gov space
  - `cf create-space staging-egress -o gsa-18f-tock`
- git clone [GSA-TTS/cf-egress-proxy](https://github.com/GSA-TTS/cg-egress-proxy)
- build the Caddy proxy (optional, not needed anymore)
  - `make caddy-v2-with-forwardproxy`)
  - note: requires Docker
- rename `vars.myapp.yml` to `vars.tock.yml`
  - configure `proxyname`, `hostname`, `username` and `password`
  - configure with above proxy rules
- `cf target -s staging-egress`
- `cf push --vars-file vars.tock.yml`
- enable tock staging to connect to tock egress
  - `cf add-network-policy tock-staging staging-egress -s staging-egress`

At this stage it is prudent to verify that the proxy is working as advertised. One way is to login tock staging and run commands such as `curl -x "https://<username>:<password>@<egress-host>.apps.internal:8080" restricted-domain.com` and make sure Caddy returns a `403 Forbidden`. Once everything looks good:

- set the proxy environment variables on tock staging
  - Note: for testing purposes only!
    - `cf set-env tock-staging http_proxy https://<username>:<password>@<egress-host>.apps.internal:8080`
    - `cf set-env tock-staging https_proxy https://<username>:<password>@<egress-host>.apps.internal:8080`
  - Once testing is complete:
    - `cf unset-env tock-staging http_proxy`
    - `cf unset-env tock-staging https_proxy`

## SSL certificates

The Python [certifi](https://pypi.org/project/certifi/) library does _not_ pick up on system-wide certificate authority files automatically. In order for a Tock (or Django) app to accept the SSL certificate which comes from the proxy, the relevant cloud.gov certificate authority must be added programmatically. A [provided script](../bin/update-ca.py) is run every time Tock is deployed. Please note that this script will only work within cloud.gov apps, due to an hard-coded path (`/etc/cf-system-certificates`).
