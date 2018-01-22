#/bin/sh

set -o errexit
set -o pipefail

cd ../tock
python manage.py migrate --settings=tock.settings.production --noinput
python manage.py collectstatic --settings=tock.settings.production --noinput
gunicorn -k gevent -w 2 tock.wsgi:application
