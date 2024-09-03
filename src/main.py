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
from PIL import Image
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


@app.post("/")
async def ocr(file: UploadFile = File(...), format: Optional[str] = None):
    # print("Content type:", file.content_type)
    print("Filename:", file.filename)
    ext = Path(file.filename).suffix.lower()
    try:
        formatted_result = []
        base64_image = None
        # Convert the image to a numpy array
        if ext in ['.jpg', '.png']:
            buffer = io.BytesIO(await file.read())

            img = Image.open(buffer)
            img_array = np.array(img)

        elif ext == ".pdf":
            img = convert_from_bytes(await file.read())
            # new_height = 800
            # img = img.resize((int(img.width * new_height / img.height), new_height))
            # import pdb; pdb.set_trace()
            img_array = np.array(img[0])
            # TODO: combined all page to y dimension

            # Convert the image to base64 for returning in the response
            buffered = io.BytesIO()
            img[0].save(buffered, format="PNG")
            base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

        else:
            json_response = {
                'msg': 'Failed',
                'status': '400'
            }
            raise HTTPException(status_code=400, detail=json.dumps(json_response))
        
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

        # If a PDF was processed, add the base64 image to the response
        if base64_image:
            json_response['image_base64'] = base64_image

    except Exception as e:
        json_response = {
            'msg': str(e),
            'results': [[]],
            'status': '500'
        }
        raise HTTPException(status_code=500, detail=json.dumps(json_response))

    return json_response
