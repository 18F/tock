FROM python:3.4

COPY requirements.txt requirements-dev.txt /tock/

WORKDIR /tock

RUN pip install -r requirements.txt -r requirements-dev.txt
