#/bin/bash

set -o errexit
set -o pipefail

cd tock

# Only run migrations on the zeroth index when in a cloud.gov environment
if [[ -v CF_INSTANCE_INDEX && $CF_INSTANCE_INDEX == 0 ]]
then
  python manage.py migrate --settings=tock.settings.production --noinput
fi

python manage.py collectstatic --settings=tock.settings.production --noinput
gunicorn -k gevent -w 2 tock.wsgi:application
