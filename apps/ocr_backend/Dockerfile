FROM python:3.10-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

COPY apps/pyproject.toml /app/pyproject.toml
COPY apps/uv.lock /app/uv.lock
RUN uv sync --no-cache --group ocr-backend --group migration

COPY apps/ocr_backend /app/ocr_backend
COPY apps/src /app/src
COPY alembic.ini /app/
COPY apps/migration /app/migration
COPY apps/scripts /app/scripts

ENV PATH=$PATH:/app/.venv/bin/
ENV HOST=0.0.0.0
ENV PYTHONPATH=/app/
ENV PORT=5000
CMD ["./scripts/run.sh"]

FROM builder AS test
WORKDIR /app
RUN uv sync --no-cache --group test --group ocr-backend --group migration
COPY apps/tests tests
CMD ["./scripts/run.sh"]
