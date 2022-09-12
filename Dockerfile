FROM ubuntu:20.04
FROM python:3.6.9-stretch

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

CMD python app.py