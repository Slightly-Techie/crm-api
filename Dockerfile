FROM python:3.10-alpine3.18

ENV PYTHONUNBUFFERED=1 

WORKDIR /code

COPY requirements.txt /code/

RUN apk update \
    && pip install --upgrade pip \
    && pip install --no-cache-dir psycopg2-binary  \
    && pip install --no-cache-dir -r requirements.txt \
    && apk add --no-cache libpq 
    
COPY . /code/