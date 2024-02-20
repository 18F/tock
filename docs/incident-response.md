## Responding to Security Incidents

1. [Start the report process as per the TTS Handbook.](https://handbook.tts.gsa.gov/security-incidents/) Note that all incidents must be reported within one hour of their discovery.

1. Because Tock is hosted on cloud.gov, you also need to follow their [Security Incident Response Guide](https://cloud.gov/docs/ops/security-ir/).

1. If the incident impacts the availability of the Tock app, notify the Tock team in #tock-dev. A member of the Tock team will then notify Tock users by posting in #tock.


If, as a member of the Tock dev team, you need to respond to an incident reported in #tock-dev, follow the additional steps outlined below.

1. Open an issue in GitHub to track the response to the incident. Label it "investigating."

1. Follow the [cloud.gov security response process](https://cloud.gov/docs/ops/security-ir-checklist/), updating the GitHub issue as appropriate.

## CircleCI

CircleCI secrets (stored in environment variables) correspond to cloud.gov [service keys](https://docs.cloudfoundry.org/devguide/services/service-keys.html).

To rotate these secrets, it is necessary to re-create the service keys and then update the CircleCI environment variables with the new values:

- `cf delete-service-key service-account-$env-tock service-key-$env-tock`
- `cf create-service-key service-account-$env-tock service-key-$env-tock`
- Update these environment variables using the CircleCI project settings page:
  - `CF_DEPLOYER_USERNAME_$env` and `CF_DEPLOYER_PASSWORD_$env`

(where `$env` is the name of the deployment environment)
