FROM ubuntu:20.04

WORKDIR /app

ADD . /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.5 \
    python3-pip \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN pip3 install -r requirements.txt

CMD python app.py
