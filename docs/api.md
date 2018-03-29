# Tock API

[:arrow_left: Back to Tock
Documentation](https://github.com/18F/tock/tree/master/docs)

You may issue GET requests to various [endpoints](https://github.com/18F/tock/tree/master/api-docs)
via the `/api/` path with results returned as JSON objects. We use Django REST
framework's TokenAuthentication library which requires all requests to include a
token value in your request header using the following format (a cURL
command-line-based request is used for this example for getting project data
from our Tock deployment):

```sh
$ curl https://tock.18f.gov/api/projects.json -H 'Authorization: Token randomalphanumericstringed854b18ba024327'
```

To obtain your own Tock API authorization token, please visit
[#tock-dev](https://gsa-tts.slack.com/messages/tock-dev/) on Slack and ping a
Tock Developer.

To access similar data in CSV format from within Tock, please visit the
[/reports](https://tock.18f.gov/reports) page.

# Usage

The Tock API is used in various ways by Tock Administrators and Tock Users.
Below are some examples of Tock API usage.

- [AngryTock Slack Bot](https://github.com/18F/angrytock)
- [Google App Script](https://github.com/18F/tock-gas-ts)
