FROM ubuntu:20.04

WORKDIR /app

ADD . /app

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install python3 -y
RUN apt-get install python3-pip -y
RUN pip install -r requirements.txt

CMD python3 app.py
