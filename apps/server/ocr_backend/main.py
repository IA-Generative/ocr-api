import os

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from .routers.auth import router as auth_router
from .routers.task import router as task_router
from .routers.health import router as health_router
from .routers.jobs import router as job_router
from .routers.text import text_router
from .routers.process import process_router
from .routers.openwebui import openwebui_router
from starlette.middleware.base import BaseHTTPMiddleware

# from .routers.template import template_router
from src import __version__
from src.config import KeycloakSettings, SentrySettings
from src.logger import logger

_environment = os.getenv("ENVIRONMENT", "production")
_sentry_settings = SentrySettings()
_keycloak_settings = KeycloakSettings()
if _sentry_settings.SENTRY_API_DSN and _environment != "testing":
    try:
        sentry_sdk.init(
            dsn=_sentry_settings.SENTRY_API_DSN,
            send_default_pii=_sentry_settings.SEND_DEFAULT_PII,
            environment=_environment,
        )
    except Exception as e:
        logger.warning(f"Sentry initialization failed, continuing without it: {e}")

app = FastAPI(
    title="MIrAI OCR API",
    version=__version__,
    description=(
        "OCR/document extraction API: upload a file (or a YouTube URL) as a job, poll or "
        "wait for it to complete, then pull the extracted text/structured content.\n\n"
        "Authenticate with an `Authorization: Bearer <API key>` header on the `Jobs`/"
        "`Process`/`Tasks`/`Text` routes."
    ),
    docs_url="/api/docs",
    redoc_url="/api/redocs",
    openapi_url="/api/openapi.json",
    openapi_tags=[
        {"name": "Jobs", "description": "Create OCR/extraction jobs from a file or a YouTube URL."},
        {
            "name": "Process",
            "description": "One-shot upload-and-wait endpoint (OpenWebUI-style): "
            "combines creating a job and waiting for its result in a single call.",
        },
        {"name": "Tasks", "description": "Look up, list, and delete jobs (called tasks once created)."},
        {"name": "Text", "description": "Pull a completed task's output as plain text, form fields, or CSV."},
        {"name": "Health", "description": "Liveness/readiness check for this API and its dependencies."},
        {
            "name": "Auth",
            "description": "Backend-for-frontend (BFF) Keycloak session for the browser SPA. Not "
            "usable from a script/API client - see the `Jobs`/`Tasks`/etc. routes for "
            "the `Authorization: Bearer <API key>` alternative.",
        },
    ],
)
Instrumentator().instrument(app).expose(app)

app.add_middleware(
    CORSMiddleware,
    # `allow_origins=["*"]` with `allow_credentials=True` is rejected by browsers for
    # credentialed requests (the BFF session cookie) - the frontend origin must be explicit.
    allow_origins=[_keycloak_settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0, private"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        response.headers["Surrogate-Control"] = "no-store"
        return response


app.add_middleware(NoCacheMiddleware)

app.include_router(auth_router, prefix="/api/auth")
app.include_router(task_router, prefix="/api")
app.include_router(health_router, prefix="/api")
app.include_router(job_router, prefix="/api")
app.include_router(text_router, prefix="/api")
app.include_router(process_router, prefix="/api")
app.include_router(openwebui_router, prefix="/api/v1/openwebui")
# app.include_router(template_router, prefix="/api")
