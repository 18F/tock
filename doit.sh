docker-compose down
docker-compose build
docker-compose run app python manage.py migrate
docker-compose run app python manage.py loaddata test_data/data-update-deduped.json
docker-compose run app \
  python manage.py \
      createsuperuser \
      --username admin.user \
      --email admin.user@gsa.gov \
      --noinput

docker-compose up
