FROM python:3.10-alpine3.18

ENV PYTHONUNBUFFERED=1 

WORKDIR /code

COPY requirements.txt /code/

RUN apk update --no-cache \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir psycopg2-binary  \
    && pip install --no-cache-dir -r requirements.txt \
    && apk add --no-cache libpq \
    && apk add --no-cache \
    build-base cairo-dev cairo cairo-tools 
    
COPY . /code/

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]