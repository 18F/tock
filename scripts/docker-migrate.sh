docker-compose start db
docker-compose run tock python manage.py migrate --settings=tock.settings.dev --noinput
