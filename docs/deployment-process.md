## Deploying to Cloud Foundry

[:arrow_left: Back to Tock Documentation](../docs)

**This section is only of interest to 18F team members.**

Download the Cloud Foundry CLI according to the [cloud.gov instructions][].

[cloud.gov instructions]: https://cloud.gov/docs/getting-started/setup/#set-up-the-command-line

We use the V7 Cloud Foundry CLI. If you're upgrading from V6, checkout [the CLI docs for instructions](https://github.com/cloudfoundry/cli).

Tock will be deployed to the GovCloud instance of cloud.gov:

```shell
# Login to cloud.gov
cf login -a api.fr.cloud.gov --sso
```

After authenticating, you'll need to target the org and space you want to work with. For example, if you wanted to work with the staging space:

```
cf target -o gsa-18f-tock -s staging
```

Manifest files, which contain import deploy configuration settings, are located
in the root directory of this project, prefixed with `manifest-` and ending in a
`.yml` file extension.

During local development and continuous integration testing,
`pipenv install --dev` is used. This installs both development
and production dependencies.

### Cloud Foundry structure

- cloud.gov environment: `GovCloud`
- Organization: `gsa-18f-tock`
- Spaces: `staging`, `staging-egress`, `prod`, `prod-egress`
- Apps:
  - `staging` space:
    - `tock-staging`
  - `staging-egress` space:
    - `staging-egress`
  - `prod` space:
    - `tock`
  - `prod-egress` space:
    - `production-egress`
- Routes:
  - tock.app.cloud.gov -> `staging` space, `tock-staging` app
  - tock.18f.gov -> `prod` space, `tock` app

#### Cloud Foundry environment variables

In production, Tock requires a few different environment variables. These values are
updated using the [User Provided Service](#user-provided-service-ups),
configured in the `manifest-*.yaml`, or set manually during [egress proxy setup](egress.md).

| type | name | description |
| ---- | -----| ----------- |
| **secret** | `DJANGO_SECRET_KEY` | The secret key used to maintain session state. Changing this value will invalidate all user sessions for Tock and log out all users.|
| **secret** | `NEW_RELIC_LICENSE_KEY` | The New Relic license key connected to the New Relic account for the application. |
| **secret** | `NEW_RELIC_API_KEY` | The New Relic API key connected to the New Relic account for the application. |
| **secret** | `UAA_CLIENT_ID` | The UAA Client ID from the cloud.gov identity provider service key. |
| **secret** | `UAA_CLIENT_SECRET` | The UAA Client Secret from the cloud.gov identity provider service key. |
| **public** | `NEW_RELIC_CONFIG_FILE` | The New Relic configuration file used by the `newrelic-admin` commands and New Relic libraries. |
| **public** | `NEW_RELIC_APP_NAME` | The application name that appears in the New Relic interface. Changing this will change will cause New Relic data to be gathered under a different application name. |
| **public** | `NEW_RELIC_ENV` | The application environment that appears in the New Relic interface. |
| **public** | `NEW_RELIC_HOST` | The New Relic endpoint used to collect APM data from the Python agent. Per [New Relic documentation](https://docs.newrelic.com/docs/security/security-privacy/compliance/fedramp-compliant-endpoints/#apm-endpoints), the default endpoint will not ensure FedRAMP compliance. |
| **public** | `NEW_RELIC_LOG` | Logging that New Relic should listen to: e.g. `stdout`. |
| **egress** | `egress_proxy` | The URL of the egress proxy used to filter external network traffic. Set manually during egress proxy setup. |
| **egress** | `http_proxy` | Set to the value of `egress_proxy`. Used to filter HTTP traffic. |
| **egress** | `https_proxy` | Set to the value of `egress_proxy`. Used to filter HTTPS traffic. |
| **egress** | `NEW_RELIC_PROXY_HOST` | Set to the value of `egress_proxy`. Specifies the proxy URL for the New Relic Python agent and admin tool. |

Variables with the designation **secret** are stored in the `tock-credentials` User-Provided Service (UPS).
**Public** variables are stored in the environment's `manifest-*.yml` file.
Variables marked **egress** are set based on manual configuration during [egress proxy setup](egress.md).

### Services

#### User-provided service (UPS)

For cloud.gov deployments, this project makes use of a [user-provided service (UPS)][UPS] to get its sensitive configuration
variables. It uses the local environment only for some [New Relic-related environment variables](#new-relic-environment-variables).

You will need to create a UPS called `tock-credentials`, provide 'credentials' to it, and link it to the
application instance. Please note that you'll need to do this for every Cloud Foundry `space`.

Once you've completed those steps, enter the following commands (filling in the main application instance name
for `<APP_INSTANCE>`) to create the user-provided service:

```sh
# Creating and uploading the credentials to the service
cf cups tock-credentials -p credentials-<ENVIRONMENT>.json

# Binding the service to the app
cf bind-service <APP_INSTANCE> tock-credentials

# Restaging the app to make use of the updated credentials.
cf restage <APP_INSTANCE> --strategy rolling
```

You can update the user-provided service with the following commands:

```sh
# Uploading the new credentials to the service
cf uups tock-credentials -p credentials-staging.json

# Restaging the app to make use of the updated credentials.
cf restage <APP_INSTANCE> --strategy rolling
```

#### Database service

Tock uses PostgreSQL for its database.

```sh
cf create-service aws-rds shared-psql tock-database
cf bind-service <APP_INSTANCE> tock-database
```

#### cloud.gov identity provider service

Tock uses the cloud.gov identity provider service to provide authentication via the
cloud.gov UAA application for its users.


#### cloud.gov service account

Tock uses the cloud.gov service account service to provide deployer accounts for
staging and production environments.

### New Relic configuration

Basic New Relic configuration is done in [newrelic.ini](../newrelic.ini), with additional settings
specified via environment variables in each deployment environment's manifest file.

As described in [Environment variables](#cloud-foundry-environment-variables), you will need
to supply the `NEW_RELIC_LICENSE_KEY` as part of each deployment's
[user-provided service](#user-provided-service-ups).

### Code review

Submissions to the Tock codebase are made via GitHub, and are only accepted into the main
branch after review. At least one approving review is required before a branch is merged
to main, and this restriction is enforced by Tock's GitHub settings.
Your reviewer will usually merge the branch for you.

Code review covers both code (such as Python or JavaScript) and configuration (such as
Dockerfiles, CloudFoundry manifest files, etc.).

Code reviews should be conducted [following the 18F Engineering Guide](https://engineering.18f.gov/code-review/) and include an assessment of:

- Simplicity. Ideally the submission implements the feature/fix with as little complexity as possible.
- Legibility. Ideally the submission is easy to understand.
- Security. The submission is reviewed for security considerations.

Code review is in addition to the various automated checks, which include tests, linting,
and checks on security flaws of Tock's dependencies.

### CircleCI continuous integration, delivery, and deployment

Tock uses CircleCI to continuously integrate code, deliver the code to staging
servers, and deploy the latest release to production servers.

#### Job output

For each job in a CircleCI workflow, you can view the output of each step in the CircleCI:

- Navigate to the CircleCI project dashboard for this organization.
- Click "Projects" in the left nav, then click "tock".
- On the project page, click the "Workflow" link for the workflow run you're interested in. For a PR build, the workflow is named "build_pull_requests".
- Click on the job (for example, "build") that you want to view.
- On the job page, expand the accordion for each step to view its output.

#### Enable verbose logging

To troubleshoot issues within a CircleCI workflow, it may be helpful to configure the project to log more verbose output.

##### Jest and Puppeteer test configuration

In the [jest-puppeteer.config.js](../jest-puppeteer.config.js) file's `module.exports` -> `launch` section:

- Add `'--enable-logging', '--v=1'` to the `args` array
- To log Chrome driver messages to console, add `dumpio: true`

Within `*.test.js` test files, use `console.log()` calls to output debugging information.

##### CircleCI jobs

In [`.circleci/config.yml`](../.circleci/config.yml), add additional steps to output information about the Docker container environment. For example:

```yml
# Add this to jobs -> <job name> -> steps
- run:
    name: Report Python, Node, and Chrome versions
    command: |
      python --version
      node --version
      google-chrome --version
```

#### Update the CircleCI project cache

Occasionally CircleCI builds will fail with an error like: `FileNotFoundError: [Errno 2] No such file or directory: '/home/circleci/project/.venv/bin/python'.` In this case, it is necessary to modify the `CACHE_VERSION` in the Environment Variables section in the CircleCI Tock Project Settings. (The exact value does not matter, just that the value is changed: this will force new cache dependencies to be built.)


### Staging server

The staging server updates automatically when changes are merged into the
`main` branch. Check out the `workflows` sections of
the [CircleCI config](../.circleci/config.yml) for details and settings.

Should you need to, you can push directly to tock.app.cloud.gov with the following:

```sh
cf target -o gsa-18f-tock -s staging
cf push tock-staging -f manifest-staging.yml --strategy rolling
```

### Production servers

Production deploys are also automated. They rely on the creation of a Git tag to
be made against the `main` branch following the [_Automated Releases to
Production_](#automated-releases-to-production) workflow.

In some cases, you may need to make a manual deployment to production. If this is the case, please make
sure you're using the rolling deployment strategy with `--strategy rolling`

To deploy, first make sure you're targeting the prod space:

```sh
cf target -o gsa-18f-tock -s prod
```

Create a `VERSION` file with the name of the version that is being deployed to
production either with the Git SHA1 for the latest commit or the Git tag for the
latest release:

```sh
# Manually creating a VERSION file from the latest Git SHA1 commit
echo $(git rev-parse HEAD | head -c 7) > tock/VERSION

# Manually creating a VERSION file from the latest Git Tag release
echo $(git describe --abbrev=0 --tags) > tock/VERSION
```

Then use the CLI to deploy:

```sh
cf push tock -f manifest-production.yml --strategy rolling
```

#### Troubleshooting failed deployments

If at any point the deployment fails, we can use the CLI to recover to our previous state.

https://docs.cloudfoundry.org/devguide/deploy-apps/rolling-deploy.html#cancel

```
cf cancel-deployment tock
```

### Logs

Logs in cloud.gov-deployed applications are generally viewable by running
`cf logs <APP_NAME> --recent`.

[UPS]: https://docs.cloudfoundry.org/devguide/services/user-provided.html
[`README.md`]: https://github.com/18F/tock#readme

## Releasing Tock

Releasing Tock onto Production happens whenever you create a Git tag and push it
up to the repository. The process is outlined in the `Creating a GitHub release` section.

You can manually create Git tags using the Git CLI as outlined in the next section. You can
also create them in the GitHub release interface when drafting and publishing
the release.

To create a new tag in the GitHub release interface (and skip the Git tag CLI step):

- Click the tag name dropdown located above the release title text input.
- Type the name of your new tag, be sure to follow the tag naming guidelines of using
a `v` followed by the full year, full month, and full day, followed by a period
and a version number for that release. For example: `v20211008.1`
- Click the "+ Create new tag: `v20211008.1` on publish" link that appears below your
newly named tag.

## Creating a GitHub release

<details>
<summary>GitHub Release Template</summary>

```markdown
### For Those About To Tock

#### Liner Notes, XX/XX/XXXX

<!-- Summary of changes -->
---

##### Stuff You Can See:

<!-- List items of changes with PR links -->
<!-
  - Example: - None. PR: [#1987](https://www.youtube.com/watch?v=dQw4w9WgXcQ&allow=autoplay)
-->
-

---

##### Admin-only Features:

<!-- List items of changes with PR links -->
<!-
  - Example: - None. PR: [#1987](https://www.youtube.com/watch?v=dQw4w9WgXcQ&allow=autoplay)
-->
-

---

##### Under The Hood:

<!-- List items of changes with PR links -->
<!-
  - Example: - None. PR: [#1987](https://www.youtube.com/watch?v=dQw4w9WgXcQ&allow=autoplay)
-->
-

---

##### Code Contributors for this release

Team Tock would like to thank:

<!-- List folks not on the Tock team who contributed commits / code -->
<!-
  - @username
-->
-
```

</details>

#### Automated releases to production

Tock is automatically deployed to Production using CircleCI, GitHub
releases, and Git tags. Tags are versioned using the following structure: the
letter `v` followed by the full year, full month, and full day, followed by a period
and a version number for that release. For example:

```sh
# Create the tag
git tag v20180131.1

# Push the tags up to GitHub
git push --tags
```

If you need to release multiple versions in a single day, increment the
number after the period (e.g., `v20180131.1` turns into `v20180131.2`).

Once you push this tag up to GitHub, draft or assign it to an already
drafted release in GitHub. CircleCI will deploy this tag to the Production
instance of Tock.


## Maintenance Mode
A simple static application exists to display a maintenance
page if/when Tock needs to be taken offline.

To show the maintenance page you will need to manually map Tock's production
route to this application.
```sh
cf target -o gsa-18f-tock -s prod
cf map-route tock-maintenance tock.18f.gov
```

Upon a new automatic release, the production route will be mapped back to the production app.

To manually re-map the route and exit "maintenance mode":
```sh
cf target -o gsa-18f-tock -s prod
cf map-route tock tock.18f.gov
```
To deploy this static application:

1. `cd` into ./tock/maintenance_page/
2. run `cf push`
