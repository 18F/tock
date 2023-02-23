# Joining the Tock team

[:arrow_left: Back to Tock Documentation](../docs)

## Onboarding

When you join the Tock team, the Tock system owner will guide you through the
onboarding checklist. The Tock product owner may schedule check-in time with you
to ensure that you're progressing and aren't stuck. If another Tock
developer is already on the project, you'll be paired with them so they can help you with onboarding-related tasks.

## Team member checklist
Before you get started onboarding, your Tock developer partner needs to take care of a few things.
They will [create a new issue](https://github.com/18f/tock/issues/new) with the following
checklist, work through it with you.
- [ ] Generate a Tock API authorization token in the admin for the new developer.
- [ ] Grant access to New Relic.
- [ ] Grant access to the GitHub repository.
- [ ] Grant access to SpaceDeveloper roles on Cloud.gov for `staging` and `prod` spaces within the  `gsa-18f-tock` org.
- [ ] Send invitation to #tock-dev in Slack.
- [ ] Grant access to `GSA_TE_TockLibrary` and `GSA_TE_UtilitiesLibrary` scripts.
- [ ] Grant access to `gsa-18f-tock` org on Snyk.


## New developer checklist
You will need to be sure you have:
- [ ] Familiarized yourself with the systems and scripts your onboarding partner has granted access to
- [ ] Reviewed the [Tock deployment process](https://github.com/18f/tock/tree/main/docs/deployment-process.md).


## Things to remember
- If you get questions about timecards that don't seem to be answerable from looking at the Tock code, it's probably the [Google Script Integration](../docs/google-script-integration.md).
- Tock API authorization tokens are generated within Tock itself by someone with Tock administrative privileges. Go to the Tock/Django admin views under the Tokens section and add a new token for onboarding developers. 
- The `GSA_TE_TockLibrary` and `GSA_TE_UtilitiesLibrary` scripts live in the TTS Google Drive as approved scripts. To grant access to new developers, search gdrive for them and add users by GSA email using the normal gdrive access control interface. 
- To access New Relic to view/update notifications or review monitoring data, you must be on VPN or otherwise on the GSA internal network or you will receive a HTTP 405 error. Login directly on [New Relic's website](https://newrelic.com).
- New Relic is administered as a cross-TTS service, and help with account administration, including creating new users, must be done through the #admins-newrelic slack channel.
-  User roles on Cloud.gov can be added either via the [dashboard](https://dashboard.fr.cloud.gov/home) or through the command-line interface with Cloud Foundry tools. The Cloud Foundry documentation for doing this via command-line is [here for set-space-role](https://cli.cloudfoundry.org/en-US/v7/set-space-role.html) and [here for set-org-role](https://cli.cloudfoundry.org/en-US/v7/set-org-role.html). Developers need User access to the Org and SpaceDeveloper access to the space to be able to deploy and administer Tock. If you add user roles via the Dashboard, the interface is a little odd. Click on the people icon (shown by the red arrow) ![cloud-roles-add](https://user-images.githubusercontent.com/51135391/127552454-e3ff0f01-0b0e-4313-b29d-7636a91f97a5.png) and make sure the default developer roles match this ![cloud-roles](https://user-images.githubusercontent.com/51135391/127552547-3b28ce22-4d4b-4711-bfc1-893a5f1a5add.png)
-  Both GitHub and Snyk have Tock developer groups. Here are quick links to Snyk's [project dashboard for Tock](https://app.snyk.io/org/gsa-18f-tock) and [permissions settings](https://app.snyk.io/org/gsa-18f-tock/manage/settings) for granting access to new Tock developers. Here are quick links to GitHub's [team access settings](https://github.com/18F/tock/settings/access) for granting access to new Tock developers.


## Things we maintain

- [Tock](tock-app), a Python Django framework web application comprised of multiple
  sub-apps:
  - tock — The main application
  - employees — The application that manages the employee data
  - projects — The application that manages the project data
  - hours — The application that manages the hours and reporting data
  - organizations — The application that manages organizations
  - api — The application that manages the API
  - utilization — The application that manages the utilization functionality
- [AngryTock](tock-bot) — a Golang Slack RTM-based bot
- [#tock-dev](tock-chat) — a Slack channel where Tock users come for technical
  support

[tock-app]: https://github.com/18F/tock
[tock-bot]: https://github.com/18F/angrytock
[tock-chat]: https://gsa-tts.slack.com/messages/C1JFYCX3P

### Important terminology and context

- [cloud.gov][docs-cg] — The PaaS that Tock uses to deploy all the apps
- [Postgres][docs-psql] — The database backend that the Tock application uses
- [Python][docs-python] — The language that the Tock app uses
- [Golang][docs-golang ] — The language that the AngryTock Slack bot uses
- [Django Web Framework][docs-django] — The application framework that the Tock application is
  built with
- [Django Rest Framework][docs-django-rest] — The REST framework that the Tock
  application is built with
- [Slack Real-Time Messaging (RTM) API][docs-slack-rtm] — The Slack API that AngryTock uses to
  communicate via Slack
- [cloud.gov identity provider][docs-cg-idp] — The identity provider that Tock
  uses for user authentication
- [cloud.gov service account][docs-cg-sa] — The service account that Tock uses
  for deployments
- [cloud.gov UAA authentication backend][docs-django-uaa] — The UAA client that
  the Tock application uses to leverage the cloud.gov identity provider

[docs-cg]: https://cloud.gov/docs/
[docs-cg-idp]: https://cloud.gov/docs/services/cloud-gov-identity-provider/
[docs-cg-sa]: https://cloud.gov/docs/services/cloud-gov-service-account/
[docs-psql]: https://www.postgresql.org/docs/
[docs-python]: https://docs.python.org/3/
[docs-golang]: https://golang.org/doc/
[docs-django]: https://docs.djangoproject.com/en/1.11/
[docs-django-rest]: http://www.django-rest-framework.org
[docs-django-uaa]: http://cg-django-uaa.readthedocs.io/en/latest/
[docs-slack-rtm]: https://api.slack.com/rtm
