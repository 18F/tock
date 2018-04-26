# Tock API

[:arrow_left: Back to Tock Documentation](../docs)

You may issue GET requests to various [endpoints](https://github.com/18F/tock/tree/master/api-docs)
via the `/api/` path; your results will be returned as JSON objects. We use Django REST
framework's TokenAuthentication library, which requires all requests to include a
token value in the request header using the following format:

```sh
$ curl https://tock.18f.gov/api/projects.json -H 'Authorization: Token randomalphanumericstringed854b18ba024327'
```
This example uses a cURL command-line-based request for getting project data from our Tock deployment.

To get your own Tock API authorization token, please visit
[#tock-dev](https://gsa-tts.slack.com/messages/tock-dev/) on Slack and ping a
Tock developer.

To access similar data in CSV format within Tock, please visit the
[/reports](https://tock.18f.gov/reports) page.

# Usage

Tock administrators and users use the Tock API in various ways.
Here are two common examples of Tock API usage:

- [AngryTock Slack Bot](https://github.com/18F/angrytock)
- [Google App Script](https://github.com/18F/tock-gas-ts)
