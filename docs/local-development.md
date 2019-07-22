## Getting started with local Tock development

[:arrow_left: Back to Tock Documentation](../docs)

1. Install [Docker][]. If you're on OS X, install Docker for Mac. If you're on Windows, install Docker for Windows.

1. Move into the `tock` directory at the repository root:

  ```
  $ cd tock
  ```

1. Run:

  ```shell
  docker-compose build
  docker-compose run app python manage.py migrate
  docker-compose run app python manage.py loaddata test_data/data-update-deduped.json
  docker-compose run app \
    python manage.py \
        createsuperuser \
        --username admin.user \
        --email admin.user@gsa.gov \
        --noinput
  ```

1. Once the above commands are successful, run:

  ```
  docker-compose up
  ```

  This will start up all required servers in containers and output their
  log information to stdout.

1. Visit [http://localhost:8000/][] directly to access the site.

  When prompted for an email address, enter `admin.user@gsa.gov`.

You can access the admin panel at `/admin`.

### Running static analysis tools

We run two linting tools in continuous integration:
[`flake8`](http://flake8.pycqa.org/en/latest/) for general linting of unused
variables, styles, etc., and [`bandit`](https://pypi.python.org/pypi/bandit), a
security-focused linter.

To run these tools locally, run:
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

Once you have a running set of containers, you should be able to attach to the
`tock_app` CONTAINER_ID using the following command:

```sh
docker attach $(docker container ps | grep -E 'tock_app' | awk '{ print $1 }')
```

This will drop you into the `tock_app` container. Now you can use `pdb` in your
local code and have a Python debugger.

##### Exiting the debugger

To properly exit the debugger, use the following keyboard commands within the
container: `Control + p, Control + q`, one after another.

If you mistakenly hit `Control + c`, you will kill the `tock_app` container! In
that case, restart the `tock_app` container with a `docker-compose up` command.


### Testing locally

The easiest, most reliable way to test locally is from within the docker container, 
which lets you access `manage.py`:

```
docker-compose run app bash
python manage.py test
```

### Making CSS changes

`docker-compose up` will also launch a [Node] machine that compiles the [Sass]
files in `tock/tock/static/sass` into corresponding CSS files in
`tock/tock/static/css/dist`. **The generated CSS files are not checked into
git, and you should not modify them by hand.**

You can also run the CSS build and watch scripts outside of the Docker
container. Install [Node][] (e.g., with `brew install node` on OS X), and then
install the dependencies with the following:

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

[Docker]: https://www.docker.com/
[http://localhost:8000/]: http://localhost:8000/
[Sass]: http://sass-lang.com/
[Node]: https://nodejs.org/en/
[UAA]: https://cloud.gov/docs/apps/leveraging-authentication/
