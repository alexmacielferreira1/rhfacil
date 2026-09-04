# syntax=docker/dockerfile:1
FROM python:3.14.7-slim-trixie

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 POETRY_VIRTUALENVS_CREATE=false
WORKDIR /app

RUN groupadd --system app && useradd --system --gid app --home /app app \
    && pip install --no-cache-dir poetry==2.4.1
COPY backend/pyproject.toml backend/poetry.lock ./
RUN --mount=type=cache,id=poetry-global-cache,target=/root/.cache/pypoetry,sharing=locked \
    poetry install --only main --no-root --no-interaction
COPY backend/app ./app
COPY backend/migrations ./migrations
COPY backend/alembic.ini ./alembic.ini
RUN chown -R app:app /app
USER app

EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000"]
