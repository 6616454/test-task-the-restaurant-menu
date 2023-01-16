FROM python:3.10.6 as production

WORKDIR /app

COPY poetry.lock pyproject.toml ./

RUN python -m pip install --upgrade pip \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev


COPY . /app

EXPOSE 8000

CMD sleep 5 && alembic upgrade head && python -m src.api.main