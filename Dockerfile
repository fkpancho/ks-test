FROM python:3-alpine

ENV PYTHONUNBUFFERED=1

# https://stackoverflow.com/questions/46711990/error-pg-config-executable-not-found-when-installing-psycopg2-on-alpine-in-dock


RUN apk add --update --no-cache python3 py3-pip gcc python3-dev
RUN apk add --update --no-cache musl-dev postgresql-dev
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

COPY ./requirements.txt /app/requirements.txt
COPY ./main.py /app/main.py
COPY ./src /app/src
COPY --chown=appuser:appuser ./token.json /app/token.json
COPY ./client_secret.json /app/client_secret.json

WORKDIR /app

RUN python3 -m pip install -r requirements.txt