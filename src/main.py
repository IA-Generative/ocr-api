import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers.health import router as heatlh_router
from .routers.inference import router as paddle_ocr_router


app = FastAPI(root_path=f"{os.getenv('ROOT_PATH', '')}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(heatlh_router, prefix="/health")
app.include_router(paddle_ocr_router, prefix="/v1")
