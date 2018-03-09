# tock

We use Tock to track our time. You can read more about Tock in this [blog post](https://18f.gsa.gov/2015/05/21/tockingtime/) about its features and the [handbook page](https://handbook.18f.gov/tock/) for guidance and instructions.

[![CircleCI](https://circleci.com/gh/18F/tock.svg?style=svg)](https://circleci.com/gh/18F/tock)

![Screenshot of Tock](https://github.com/18F/tock/blob/master/Screen%20Shot%202016-12-05%20at%2011.30.54%20AM.png)

If your team uses Tock and Slack, you might also find the ["angrytock" reminder bot](https://github.com/18F/angrytock) helpful.

## Getting Started

1. Install [Docker][]. If you're on OS X, install Docker for Mac. If you're on Windows, install Docker for Windows.

1. Move into the `tock` directory at the repository root:

  ```
  $ cd tock
  ```

1. Run:

  ```shell
  $ docker-compose build
  $ docker-compose run app python manage.py migrate
  $ docker-compose run app python manage.py loaddata test_data/data-update-deduped.json
  $ docker-compose run app python manage.py createsuperuser --username admin@gsa.gov --email admin@gsa.gov --noinput
  ```

1. Once the above commands are successful, run:

  ```
  docker-compose up
  ```

  This will start up all required servers in containers and output their
  log information to stdout.

1. Visit [http://localhost:8000/][] directly to access the site.

  When prompted for an email address, enter `admin@gsa.gov`.

You can access the admin panel at `/admin`.

### Running static analysis tools

We run two linting tools in continuous integration,
[`flake8`](http://flake8.pycqa.org/en/latest/) for general linting of unused
variables, style, etc. and [`bandit`](https://pypi.python.org/pypi/bandit), a
security-focused linter.

To run this locally, run:
```sh
docker-compose run app bandit -r . -x manage.py,docker_entrypoint.py
docker-compose run app flake8
```

### Accessing the app container

You'll likely want to run `manage.py` to do other things at some point.
To do this, it's probably easiest to run:

```
docker-compose run app bash
```

This will run an interactive bash session inside the main app container.
In this container, the `/tock` directory is mapped to the `tock`
directory of the repository on your host; you can run `manage.py` from there.

#### Running `pdb` within the Docker container

Once you have a running set containers, you should be able to attach to the
`tock_app` CONTAINER_ID using the following command.

```sh
docker attach $(docker container ps | grep -E 'tock_app' | awk '{ print $1 }')
```

This will drop you into the `tock_app` container. Now you can use `pdb` in your
local code and have a Python Debugger.

##### Exiting the debugger

To properly exit the debugger, use the following keyboard commands within the
container: `Control + p, Control + q` one after another.

If you mistakenly hit `Control + c` you will kill the `tock_app` container! In
that case, restart the `tock_app` container with a `docker-compose up` command.

### Making CSS changes

`docker-compose up` will also launch a [Node] machine that compiles the [Sass]
files in `tock/tock/static/sass` into corresponding CSS files in
`tock/tock/static/css/dist`. **The generated CSS files are not checked into
git, and should not be modified by hand.**

You can also run the CSS build and watch scripts outside of the Docker
container. Just install [Node][] (e.g. with `brew install node` on OS X), then
install the dependencies with:

```sh
npm install
```

Assuming that goes off without a hitch, you can then either build the CSS in
one go with:

```
npm run build-css
```

or start the watch process, which builds new CSS whenever the source Sass files
are changed:

```
npm run watch-css
```

## API

Tock has an API! You may issue GET requests to various [endpoints](https://github.com/18F/tock/tree/master/api-docs) via the /api/ path with results returned as JSON objects. We use Django REST framework's TokenAuthentication library which requires all requests to include a token value in your request header using the following format (a cURL command line based request is used for this example for getting project data from our Tock deployment):
```
$ curl https://tock.18f.gov/api/projects.json -H 'Authorization: Token randomalphanumericstringed854b18ba024327'
```
To obtain your own Tock API authorization token, please visit [#tock-dev](https://gsa-tts.slack.com/messages/tock-dev/) on Slack!

To access similar data in CSV format from within Tock, please visit the [/reports](https://tock.18f.gov/reports) page.

## Authentication

18F's current deployment of Tock relies on
[cloud.gov's User Account and Authentication (UAA) server][UAA] for
authentication.

During development, a ["fake" cloud.gov UAA server][fakeUAA] is used for
authentication. Here you can actually enter any email address; if the
address is `@gsa.gov`, then a non-staff account will automatically
be created for the user and you'll be logged-in, but otherwise access
will be denied.

The easiest way to create an administrative user is to first use
`manage.py createsuperuser` to create a user, and then log in
with that user's email address.  See the "Getting Started" section
for an example of this.

[Docker]: https://www.docker.com/
[http://localhost:8000/]: http://localhost:8000/
[Sass]: http://sass-lang.com/
[Node]: https://nodejs.org/en/
[UAA]: https://cloud.gov/docs/apps/leveraging-authentication/
[fakeUAA]: http://cg-django-uaa.readthedocs.io/en/latest/quickstart.html#using-the-fake-cloud-gov-server
