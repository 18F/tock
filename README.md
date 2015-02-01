tock
===============

A simple time tracking experiment

## Setup

This is a Django application that depends on Python 3.

### Installing Python 3
There are multiple approaches to installing Python 3, depending on your personal setup and preferences.

One option is to [pyenv](https://github.com/yyuu/pyenv) to manage downloading Python 3 or you can install them directly.

For OS X, install Homebrew](http://brew.sh) (OS X), then run `brew install Python3`. For Ubuntu, install using `apt-get install Python3`.


### Project setup

Create an environment to install Python dependencies, with virtualenvwrapper.

```bash
mkvirtualenv --python=/path/to/python3 peacecorps-site
```

Example:
```bash
mkvirtualenv --python=/usr/local/bin/python3 peacecorps-site
```

Note: You don't need to explicitly specify the Python version, especially if
you use pyenv + virtualenvwrapper. Running mkvirtualenv in that scenario will
'freeze' the currently active version of Python.

Pull down the repo:

```bash
git clone https://github.com/18F/peacecorps-site
cd peacecorps-site
```

Install project requirements:

```bash
pip install -r requirements.txt
```

### Settings

You will also need to create a `local_settings.py` file inside
tock/settings.  It should contain `SECRET_KEY` and `DATABASES`
configurations. Up-and-running defaults (using sqlite) can be found in the
test.py configuration.  See the Django settings
[documentation](https://docs.djangoproject.com/dev/ref/django-admin/) for
details.

### Loading Data

To synchronize to the latest schema, change into the `tock` directory
and then run:
```bash
python manage.py migrate
```

You will want to synchronize with the latest list of government entities for billing:

```bash
python manage.py import_agencies https://raw.githubusercontent.com/seanherron/OMB-Agency-Bureau-and-Treasury-Codes/master/omb-agency-bureau-treasury-codes.csv
```