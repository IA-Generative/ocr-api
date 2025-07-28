FROM python:3.10-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

COPY apps/server/pyproject.toml /app/pyproject.toml
COPY apps/server/uv.lock /app/uv.lock
RUN uv sync --no-cache --group ocr-backend --group migration

COPY apps/server/ocr_backend /app/ocr_backend
COPY apps/server/src /app/src
COPY alembic.ini /app/
COPY apps/server/migration /app/migration
COPY apps/server/scripts /app/scripts

ENV PATH=$PATH:/app/.venv/bin/
ENV HOST=0.0.0.0
ENV PYTHONPATH=/app/
ENV PORT=5000
CMD ["./scripts/run.sh"]

FROM builder AS test
WORKDIR /app
RUN uv sync --no-cache --group test --group ocr-backend --group migration
COPY apps/server/tests tests
CMD ["./scripts/run.sh"]
