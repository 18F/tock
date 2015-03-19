tock
===============

A simple time tracking experiment

## Getting Started

Make sure you have `vagrant` installed. For instance, on OS X with Homebrew:

```
$ brew cask install vagrant
```

Then, ensure you have the appropriate Vagrant Box installed:

```
$ vagrant box add ubuntu/trusty32
```

You can get started with development by running the `Vagrantfile`:

```
$ vagrant up
```

This will provision an entire setup for you pretty quickly (see `provision/dev/bootstrap.sh`). You can access Django and start `runserver` by doing the following:

```
$ vagrant ssh
$ cd /vagrant
$ pyenv activate tock
$ python manage.py runserver
```

From your host computer, going to http://192.168.33.10 will enable you to view Tock. You're automatically logged in as `testuser@gsa.gov`, the nginx proxy in production will pull the logged in user from Google Auth proxy. You can access the admin panel at http://192.168.33.10/admin
