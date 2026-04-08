from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from .routers.task import router as task_router
from .routers.health import router as health_router
from .routers.jobs import router as job_router
from .routers.text import text_router
from .routers.process import process_router
from .routers.annotations import router as annotations_router
from .routers.ocr_chunks import router as ocr_chunks_router
from .routers.chat import router as chat_router
from .routers.v1 import router as v1_router

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

app.include_router(task_router, prefix="/api")
app.include_router(health_router, prefix="/api")
app.include_router(job_router, prefix="/api")
app.include_router(text_router, prefix="/api")
app.include_router(process_router, prefix="/api")
app.include_router(annotations_router, prefix="/api")
app.include_router(ocr_chunks_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(v1_router, prefix="/v1")
# app.include_router(template_router, prefix="/api")
