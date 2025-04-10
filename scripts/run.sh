#!/bin/sh

set -e

export APP_MODULE=${APP_MODULE-ocr_backend.main:app}
export HOST=${HOST:-0.0.0.0}
export PORT=${PORT:-8000}
export WORKERS=${WORKERS:-2}
export DEV_MODE=${DEV_MODE:-false}

if [ "$DEV_MODE" = "true" ]; then
  echo "Dev mode launched"
  uvicorn --host $HOST --port $PORT "$APP_MODULE" --reload
else
  uvicorn --host $HOST --port $PORT "$APP_MODULE"
fi