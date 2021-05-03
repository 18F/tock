FROM python:3.9.3

RUN apt-get update && apt-get install -y postgresql-client

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pip install pipenv
RUN pipenv install --system --dev
