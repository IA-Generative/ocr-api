from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost", "0.0.0.0", "https://mirai-api.c0.cloud-pi-native.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/", response_class=PlainTextResponse)
def home():
    return "API endpoint for OCR"
