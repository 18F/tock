# tock

We use Tock to track our time. You can read more about Tock in this [blog post](https://18f.gsa.gov/2015/05/21/tockingtime/) about its features.

[![Build Status](https://travis-ci.org/18F/tock.svg)](https://travis-ci.org/18F/tock)

![Screenshot of Tock](https://18f.gsa.gov/assets/blog/tockingtime/tock03.jpg)

If your team uses Tock and Slack, you might also find the ["angrytock" reminder bot](https://github.com/18F/angrytock) helpful.

## Getting Started

**First**, install [Docker][] and [Docker Compose][]. (If you're on OS X or
Windows, you'll also have to explicitly start the Docker Quickstart Terminal,
at least until [Docker goes native][].)

**Second**, move a level down from your root `~\tock` directory (the one with the `manage.py` file):
```
$ cd tock
```
This is where the `env.sample` file is held.

**Third**, run:

```shell
$ cp .env.sample .env
$ docker-compose build
$ docker-compose run app python manage.py migrate
$ docker-compose run app python manage.py loaddata test_data/data-update.json
```

**Fourth**, once the above commands are successful, run:

```
docker-compose up
```

This will start up all required servers in containers and output their
log information to stdout. If you're on Linux, you should be able
to visit http://localhost:8000/ directly to access the site. If you're on
OS X or Windows, you'll likely have to visit port 8000 on the IP
address given to you by `docker-machine ip default`. (Note that this 
hassle will go away once [Docker goes native][] for OS X/Windows.)

You can access the admin panel at `/admin`.

If you receive an `ERROR: Couldn't connect to Docker daemon - you might need to run...` error and you have confirmed that the Docker machine is running, you may need to run:

```
$ eval "$(docker-machine env default)"
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

Note that if you don't have Django installed on your host system, you
can just run `python manage.py` directly from outside the container--the
`manage.py` script has been modified to run itself in a Docker container
if it detects that Django isn't installed.

### Making Sass changes

`docker-compose up` will also launch [Sass] and automatically compile
SCSS (`.scss`) files into CSS as you change them.

All of the files you should be editing are located in
`tock/tock/static/sass/` and are labeled according to their purpose,
e.g. `base/_typography.scss` focuses on website type stylings.

**:warning: Only change files ending in  `.scss` directly; NOT `.css`!**

## API

Tock has an API! You can get the full dataset at
[/api/timecards_bulk.csv](https://tock.18f.gov/api/timecards_bulk.csv),
page through results at [/api/timecards.json](https://tock.18f.gov/api/timecards.json),
or choose a different page or page size, e.g.
[/api/timecards.json?page=2&page_size=100](https://tock.18f.gov/api/timecards.json?page=2&page_size=100)

You can also get a list of projects at
[/api/projects.json](https://tock.18f.gov/api/projects.json),
or as a spreadsheet at [/api/projects.csv](https://tock.18f.gov/api/projects.csv).

[Docker]: https://www.docker.com/
[Docker Compose]: https://docs.docker.com/compose/
[Docker goes native]: https://blog.docker.com/2016/03/docker-for-mac-windows-beta/
[Sass]: http://sass-lang.com/
