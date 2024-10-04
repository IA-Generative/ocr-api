import base64
import io
from typing import List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fastapi import File, HTTPException, UploadFile
from paddleocr import PaddleOCR
from PIL import Image, ImageOps
import numpy as np
from pydantic import BaseModel
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
    lang="fr",
)


class Box(BaseModel):
    text: str
    text_region: List[List[int]]
    confidence: float


@app.get("/", response_class=PlainTextResponse)
def home():
    return "API endpoint for OCR"


# Helper function: Perform OCR and format result
def perform_ocr(img_array):
    result = OCRCustom.ocr(img_array)
    return (
        [
            {
                "confidence": round(confidence, 2),
                "text": text,
                "text_region": [[int(x), int(y)] for x, y in bbox],
            }
            for bbox, (text, confidence) in result[0]
        ]
        if result != [None]
        else []
    )


# Helper function: Convert image to base64
def image_to_base64(image, format="PNG"):
    buffered = io.BytesIO()
    image.save(buffered, format=format)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


@app.post("/")
async def ocr(
    file: UploadFile = File(...),
    format: Optional[str] = None,
    max_height: Optional[int] = None,
    grayscale: Optional[bool] = True,
    return_image: Optional[bool] = True,
):
    ext = Path(file.filename).suffix.lower()
    print(file.filename)
    try:
        base64_images, formatted_result = [], []
        if ext in [".jpg", ".png"]:
            pages = [Image.open(io.BytesIO(await file.read()))]
        elif ext == ".pdf":
            pages = convert_from_bytes(await file.read())
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        for page in pages:
            width, height = page.size
            # import pdb; pdb.set_trace()
            if max_height and int(height) > max_height:
                page = page.resize((int(width * max_height / height), max_height))

            if return_image:
                base64_images.append(image_to_base64(page))

            if grayscale:
                page = ImageOps.grayscale(page)

            formatted_result.append(perform_ocr(np.array(page)))

        json_response = {"msg": "Success", "results": formatted_result, "status": "200"}

        if base64_images:
            json_response["images_base64"] = base64_images

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    return json_response


@app.post("/read")
async def read(ocr_data: list[list[Box]]):
    full_text = ""
    for page in ocr_data:
        # Sort each page by y1 (top position), then by x1 (left position)
        sorted_page = sorted(
            page,
            key=lambda item: (item.text_region[0][1], item.text_region[0][0]),
        )

        page_text = ""
        last_y = None
        # Threshold to decide whether two boxes are on the same line
        line_threshold = 10

        for item in sorted_page:
            text = item.text
            x1, y1 = item.text_region[0]  # top-left corner
            # y2 can be used if needed for more precise row checking

            # Add a new line if the current box starts a new row
            if last_y is not None and abs(y1 - last_y) > line_threshold:
                page_text += "\n"

            # Concatenate the current text to the output
            if page_text and page_text[-1] != "\n":
                page_text += " "  # Separate words with a space
            page_text += text

            # Update the last_y to the current box's y1
            last_y = y1

        # Append the concatenated text of the current page to the full text
        full_text += page_text + "\n\n"  # Separate pages with a double newline
    return full_text
