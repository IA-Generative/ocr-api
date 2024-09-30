import base64
import io
from typing import List, Optional
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
from PIL import Image, ImageOps
import numpy as np
from pydantic import BaseModel
import json
from pathlib import Path
from pdf2image import convert_from_bytes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load OCR model in advance
# The path of detection and recognition model must contain model and params files

path_model = Path(__file__).parent.absolute()  # previously in /app/models

OCRCustom = PaddleOCR(
    det_model_dir=str(path_model / "detection"),
    rec_model_dir=str(path_model / "recognition"),
    cls_model_dir=str(path_model / "recognition"),
    use_angle_cls=False,
    lang="fr"
)


class ImageRequest(BaseModel):
    images: List[str]


@app.get("/", response_class=PlainTextResponse)
def home():
    return "API endpoint for OCR"


# Helper function: Perform OCR and format result
def perform_ocr(img_array):
    result = OCRCustom.ocr(img_array)
    return [{
        'confidence': confidence,
        'text': text,
        'text_region': [[int(x), int(y)] for x, y in bbox]
    } for bbox, (text, confidence) in result[0]] if result != [None] else []


# Helper function: Convert image to base64
def image_to_base64(image, format="PNG"):
    buffered = io.BytesIO()
    image.save(buffered, format=format)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


@app.post("/")
async def ocr(file: UploadFile = File(...),
              format: Optional[str] = None,
              max_height: Optional[int] = None,
              grayscale: Optional[bool] = True):
    ext = Path(file.filename).suffix.lower()
    print(file.filename)
    try:
        base64_images, formatted_result = [], []

        if ext in ['.jpg', '.png']:
            pages = [Image.open(io.BytesIO(await file.read()))]
        elif ext == ".pdf":
            pages = convert_from_bytes(await file.read())
        else:
            raise HTTPException(status_code=400, detail='Unsupported file type')

        for page in pages:
            width, height = page.size
            # import pdb; pdb.set_trace()
            if max_height and int(height) > max_height:
                page = page.resize((int(width * max_height / height), max_height))
            base64_images.append(image_to_base64(page))
            if grayscale:
                page = ImageOps.grayscale(page)
            formatted_result.append(perform_ocr(np.array(page)))

        json_response = {
            'msg': 'Success',
            'results': formatted_result,
            'status': '200'
        }

        if base64_images:
            json_response['images_base64'] = base64_images

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    return json_response
