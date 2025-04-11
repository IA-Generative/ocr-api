import base64
import io
import time
from typing import List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import File, HTTPException, UploadFile
from PIL import Image, ImageOps
import numpy as np
from pydantic import BaseModel
from pathlib import Path
import traceback
from pdf2image import convert_from_bytes
from .logger import logger
from .models.paddle import perform_ocr_async
from .routers.health import router as health_router
from . import __name__, __version__

app = FastAPI(title=__name__, version=__version__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health_router, prefix="/health")


class Box(BaseModel):
    text: str
    text_region: List[List[int]]
    confidence: float


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
    logger.debug(file.filename)
    t = time.time()
    content = await file.read()

    try:
        base64_images, formatted_result = [], []
        if ext in [".jpg", ".png"]:
            pages = [Image.open(io.BytesIO(content))]
        elif ext == ".pdf":
            t_convert = time.time()
            pages = convert_from_bytes(content)
            t_convert = time.time() - t_convert
            logger.debug(
                f"{file.filename} convert to image nb pages {len(pages)} into {t_convert}"
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        for i, page in enumerate(pages):
            width, height = page.size
            # import pdb; pdb.set_trace()
            if max_height and int(height) > max_height:
                page = page.resize((int(width * max_height / height), max_height))

            if return_image:
                base64_images.append(image_to_base64(page))

            if grayscale:
                page = ImageOps.grayscale(page)
        n = 2
        for i in range(0, len(pages), n):
            t_predict = time.time()
            batch = pages[i : i + n]

            # Si une seule image restante, empile avec une nouvelle dimension
            if len(batch) == 1:
                images = np.array(batch[0])
            else:
                images = np.stack(batch, axis=0)

            partial_result = await perform_ocr_async(images)
            formatted_result.extend(partial_result)

            page_range = f"{i+1}" if len(batch) == 1 else f"{i+1}-{i+n}"
            logger.debug(
                f"{file.filename} time to process page {page_range} - {time.time() - t_predict:.2f}s"
            )

        json_response = {"msg": "Success", "results": formatted_result, "status": "200"}

        if base64_images:
            json_response["images_base64"] = base64_images

    except Exception as e:
        logger.error(f"{str(e)} - {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    logger.debug(f"{file.filename} - processed in {time.time() - t}")
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
