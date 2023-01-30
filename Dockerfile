FROM python:3.10-slim as build_app

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

COPY poetry.lock pyproject.toml ./

RUN python -m pip install --upgrade pip && pip install poetry && poetry config virtualenvs.create false


COPY . /app


FROM build_app as prod

RUN poetry install --without dev

EXPOSE 8000

CMD alembic upgrade head && python -m src.api.main

FROM build_app as test

RUN poetry install --with dev

CMD pre-commit run --all-files && alembic upgrade head && pytest -vv



