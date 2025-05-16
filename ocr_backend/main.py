import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.task import router as task_router
from .routers.health import router as health_router
from .routers.jobs import router as job_router
from src import __name__, __version__

app = FastAPI(title=__name__, version=__version__)

cors_config = {}
path_cors_config = os.environ.get("CORS_CONFIG_PATH", "ocr_backend/config/cors.json")
if os.path.exists(path_cors_config):
    with open(path_cors_config) as config_file:
        cors_config = json.load(config_file)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=cors_config.get("allow_origin_regex", "*"),
    allow_credentials=cors_config.get("allow_credentials", True),
    allow_methods=cors_config.get("allow_methods", ["*"]),
    allow_headers=cors_config.get("allow_headers", ["*"]),
)

app.include_router(task_router)
app.include_router(health_router)
app.include_router(job_router)
