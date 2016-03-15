docker-compose run db psql -h db -U tock -c 'CREATE DATABASE IF NOT EXISTS "tock-test"'
docker-compose run tock python manage.py syncdb --noinput --settings=tock.settings.test
docker-compose run tock python manage.py test --noinput --settings=tock.settings.test
