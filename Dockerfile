FROM python:3.9

WORKDIR /code

ENV PYTHONUNBUFFERED=1 \
    POETRY_HOME="/code/poetry"

ENV PATH="$POETRY_HOME/bin:$PATH"

RUN curl -sSL https://install.python-poetry.org | python3 -

COPY poetry.lock pyproject.toml /code/

RUN poetry install

COPY . /code/

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8080"]



