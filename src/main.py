import base64, io
from typing import List
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
from pydantic import BaseModel



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
OCRCustom=PaddleOCR(
    det_model_dir='/app/models/detection',
    rec_model_dir='/app/models/recognition',
    cls_model_dir='/app/models/recognition',
    use_angle_cls=False
)

class ImageRequest(BaseModel):
    images: List[str]



@app.get("/", response_class=PlainTextResponse)
def home():
    return "API endpoint for OCR"



@app.post("/")
async def ocr(request: ImageRequest):
    try:
        formatted_result = []
        for encoded_image in request.images:
            image_data = base64.b64decode(encoded_image)
            buffer = io.BytesIO(image_data)
            # Convert the image to a numpy array
            img_array = np.array(Image.open(buffer))
            # FORMAT OF RESULT = List of elements E found on image
            # where E is a list containing
            # 1. The bbox coordinates (List of [A,B] where A,B are a corner coordinates)
            # 2. The text infos (List of [A,B] where A=Text identified and B=confidence)
            result = OCRCustom.ocr(img_array)

            for element in result[0]:
                bbox, (text, confidence) = element
                formatted_result.append({
                    'confidence': confidence,
                    'text': text,
                    'text_region': [[int(x), int(y)] for x, y in bbox]
                })

        json_response = {
            'msg': 'Success',
            'results': [formatted_result],
            'status': '200'
        }

    except Exception as e:
        json_response = {
            'msg': str(e),
            'results': [[]],
            'status': '500'
        }

    return json_response
