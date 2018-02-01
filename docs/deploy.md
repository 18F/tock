## Deploying to Cloud Foundry

**This section is only of interest to 18F team members.**

Download the Cloud Foundry CLI according to the [cloud.gov instructions][].

[cloud.gov instructions]: https://docs.cloud.gov/getting-started/setup/

You will also need to install the [`autopilot`](https://github.com/contraband/autopilot)
plugin for Cloud Foundry, which is used for zero-downtime deploys.
You can install via
`cf install-plugin autopilot -f -r CF-Community`.

Tock is deployed to the GovCloud instance of cloud.gov. You will need to login
to via the GovCloud api of cloud.gov:
`cf login -a api.fr.cloud.gov --sso`

Then target the org and space you want to work with. For example, if you wanted to work with the dev space:
`cf target -o gsa-18f-tock -s dev`

Manifest files, which contain import deploy configuration settings, are located
in the root directory of this project, prefixed with `manifest-` and ending in a
`.yml` file extension.

Note that this project has two requirements files:
* `requirements.txt` for production dependencies
* `requirements-dev.txt` for development and testing dependencies

During local development and continuous integration testing,
`pip install -r requirements-dev.txt` is used, which installs both
development and production dependencies. During deployments, the Cloud
Foundry python buildpack uses only `requirements.txt` by default, so
only production dependencies will be installed.

### Cloud Foundry structure

- cloud.gov environment: `GovCloud`
- Organization: `gsa-18f-tock`
- Spaces: `staging`, `prod`
- Apps:
  - `staging` space:
    - `tock-staging`
  - `prod` space:
    - `tock`
- Routes:
  - tock.app.cloud.gov -> `staging` space, `tock-staging` app
  - tock.18f.gov -> `prod` space, `tock` app

### Services

#### User Provided Service (UPS)

For cloud.gov deployments, this project makes use of a [User Provided Service (UPS)][UPS] to get its configuration
variables, instead of using the local environment (except for [New Relic-related environment variables](#new-relic-environment-variables)).
You will need to create a UPS called `tock-credentials`, provide 'credentials' to it, and link it to the
application instance. This will need to be done for every Cloud Foundry `space`.

<!--
First, create a JSON file (e.g. `credentials-staging.json`) with all the configuration values specified as per the
[Environment variables](environment.md). **DO NOT COMMIT THIS FILE.**

```json
{
  "SECRET_KEY": "my secret key",
  "...": "other environment variables"
}
```
-->

Then enter the following commands (filling in the main application instance name
for `<APP_INSTANCE>`) to create the user-provided service:

```sh
cf cups tock-credentials -p credentials-<ENVIRONMENT>.json
cf bind-service <APP_INSTANCE> tock-credentials
cf restage <APP_INSTANCE>
```

You can update the user-provided service with the following commands:

```sh
cf uups tock-credentials -p credentials-staging.json
cf restage <APP_INSTANCE>
```

#### Database service

Tock uses PostgreSQL for its database.

```sh
cf create-service aws-rds shared-psql tock-database
cf bind-service <APP_INSTANCE> tock-database
```

### New Relic environment variables

Basic New Relic configuration is done in [newrelic.ini](../newrelic.ini), with
additional settings specified in each deployment environment's manifest file.

As described in [Environment variables](environment.md), you will need
to supply the `NEW_RELIC_LICENSE_KEY` as part of each deployment's
[User Provided Service](#user-provided-service-ups).

### Staging server

The staging server updates automatically when changes are merged into the
`master` branch. Check out the `workflows` sections of
the [CircleCI config](../.circleci/config.yml) for details and settings.

Should you need to, you can push directly to tock.app.cloud.gov with:

```sh
cf target -o gsa-18f-tock -s staging
cf push -f manifest-staging.yml
```

### Production servers

Production deploys are a somewhat manual process in that they are not done
from CI. However, just like in our CircleCI deployments to staging, we use the
Cloud Foundry [autopilot plugin](https://github.com/contraband/autopilot).

To deploy, first make sure you are targeting the prod space:

```sh
cf target -o gsa-18f-tock -s prod
```

Now, if you don't already have the autopilot plugin, you can install it by running:

```sh
cf install-plugin autopilot -f -r CF-Community
```

Then use the autopilot plugin's `zero-downtime-push` command to deploy:

```sh
cf zero-downtime-push tock -f manifest-production.yml
```

<!--
If a breaking database migration needs to be done, things get a little trickier because
the database service is actually shared between the two production apps. If the migration
breaks the current version of Tock, we'll need to have a (hopefully short) amount of downtime.

We have a very simple maintenance page application that uses the CloudFoundry staticfiles
buildpack. This app is in the [maintenance_page](../maintenance_page/) subdirectory.

If `<APP_NAME>-maintenance` is not running or has not been deployed yet:

```sh
cd maintenance_page
cf push
```

Once `<APP_NAME>-maintenance` is running:

```sh
cf map-route <APP_NAME>-maintenance tock.18f.gov
cf unmap-route <APP_NAME>-prod
```

And then deploy the production app:

```sh
cf push -f manifests/manifest-prod.yml
```

One the deploy is successful:

```sh
cf map-route <APP_NAME>-prod tock.18f.gov
cf unmap-route <APP_NAME>-maintenance
```
-->

### Logs

Logs in cloud.gov-deployed applications are generally viewable by running
`cf logs <APP_NAME> --recent`

[UPS]: https://docs.cloudfoundry.org/devguide/services/user-provided.html
[`README.md`]: https://github.com/18F/tock#readme

### Automated Releases to Production

Tock is automatically deployed to Production using CircleCI using GitHub
Releases and Git tags. Tags are versioned using the following structure, the
letter `v` followed by the full year, full month, full day, followed by a period
and last a version number for that release. For example:

```
v20180131.1
```

Once this tag is pushed up to GitHub, you can draft or assigned to an already
drafted release and CircleCI will deploy this tag to the Production instance of
Tock using CF Autopilot.
