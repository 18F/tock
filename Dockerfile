FROM python:3.5.2

COPY requirements.txt requirements-dev.txt /tock/

WORKDIR /tock

RUN pip install -r requirements.txt -r requirements-dev.txt
