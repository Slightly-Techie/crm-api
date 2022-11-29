FROM python:3.9

WORKDIR /code

COPY requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./api /code/src

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8080"]



# db_url = postgres://postgres:WGod4JQZFZoFwai@crm-db.internal:5432