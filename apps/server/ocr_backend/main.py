from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi_mcp import FastApiMCP, AuthConfig

from .mcp_compat import patch_fastapi_mcp_recursion

from .routers.task import router as task_router
from .routers.health import router as health_router
from .routers.jobs import router as job_router
from .routers.text import text_router
from .routers.process import process_router
from .routers.annotations import router as annotations_router
from .routers.ocr_chunks import router as ocr_chunks_router
from .routers.chat import router as chat_router
from .routers.v1 import router as v1_router
from ocr_backend.core.security.factory import TokenVerifier

# from .routers.template import template_router
from src import __name__, __version__

app = FastAPI(
    title=__name__,
    version=__version__,
    docs_url="/api/docs",
    redoc_url="/api/redocs",
    openapi_url="/api/openapi.json",
)
Instrumentator().instrument(app).expose(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

_secure = [Depends(TokenVerifier)]

app.include_router(task_router, prefix="/api", dependencies=_secure)
app.include_router(health_router, prefix="/api")
app.include_router(job_router, prefix="/api", dependencies=_secure)
app.include_router(text_router, prefix="/api", dependencies=_secure)
app.include_router(process_router, prefix="/api", dependencies=_secure)
app.include_router(annotations_router, prefix="/api", dependencies=_secure)
app.include_router(ocr_chunks_router, prefix="/api", dependencies=_secure)
app.include_router(chat_router, prefix="/api", dependencies=_secure)
app.include_router(v1_router, prefix="/api/v1", dependencies=_secure)
# app.include_router(template_router, prefix="/api")


# Expose all API routes as MCP tools.
# The MCP server is mounted on the same app and reuses the existing
# `TokenVerifier` dependency: the client's `Authorization: Bearer <token>`
# header is passed through to the underlying endpoints (token passthrough).
# `patch_fastapi_mcp_recursion` makes the OpenAPI -> MCP conversion resilient to
# self-referential Pydantic models (e.g. `TableHeader`, `TableCell`).
patch_fastapi_mcp_recursion()
mcp = FastApiMCP(
    app,
    name=__name__,
    description=f"MCP server exposing the {__name__} API endpoints as tools.",
    auth_config=AuthConfig(
        dependencies=_secure,
    ),
)
mcp.mount_http(mount_path="/api/mcp")
