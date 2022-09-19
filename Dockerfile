FROM ubuntu:20.04

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

CMD python app.py
