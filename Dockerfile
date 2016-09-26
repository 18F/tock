FROM python:3.5.2

COPY requirements.txt requirements-dev.txt /tock/

RUN pip install -r /tock/requirements.txt -r /tock/requirements-dev.txt
