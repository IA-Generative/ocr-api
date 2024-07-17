import base64, io
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, FileResponse
from fastapi import (
    File,
    Form,
    HTTPException,
    Request,
    Response,
    UploadFile,
    Body
)
from paddleocr import PaddleOCR
from PIL import Image
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost", "0.0.0.0", "https://mirai-api.c0.cloud-pi-native.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load OCR model in advance
# The path of detection and recognition model must contain model and params files
OCRCustom=PaddleOCR(
    det_model_dir='/app/models/detection',
    rec_model_dir='/app/models/recognition',
    cls_model_dir='/app/models/recognition',
    use_angle_cls=False
)



@app.get("/", response_class=PlainTextResponse)
def home():
    return "API endpoint for OCR"



@app.post("/")
async def ocr(image: str = Body(..., embed=True)):
    image_data = base64.b64decode(image)
    buffer = io.BytesIO(image_data)
    # Open the image using PIL
    img = Image.open(buffer)
    # Convert the image to a numpy array
    img_array = np.array(img)
    print(img_array.shape)
    result = OCRCustom.ocr(img_array)
    for line in result:
        print(line)
    return result