FROM python:3.4
MAINTAINER Mila Frerichs mila@civicvision.de

RUN mkdir /tock
WORKDIR /tock

COPY requirements.txt /tock
COPY requirements-dev.txt /tock

RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt

COPY tock /tock

EXPOSE 4001

CMD ["waitress-serve", "--port=4001", "tock.wsgi:application"]
