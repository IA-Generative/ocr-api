import base64
import io
from typing import Optional, List
from fastapi import APIRouter
from fastapi import File, HTTPException, UploadFile
from PIL import Image, ImageOps
import numpy as np
from pathlib import Path
from pdf2image import convert_from_bytes
from ..schemas.box import Box
from ..schemas.inference import PaddleOCRResult, TextBox
from ..services.paddle_ocr import OCRCustom, image_to_base64

router = APIRouter()

ocr_model = OCRCustom()


@router.post("/")
async def ocr(
    file: UploadFile = File(...),
    format: Optional[str] = None,
    max_height: Optional[int] = None,
    grayscale: Optional[bool] = True,
    return_image: Optional[bool] = True,
):
    ext = Path(file.filename).suffix.lower()
    page_ids: List[int] = []

    try:
        base64_images: List[str] = []

        page_list = []
        if ext in [".jpg", ".png"]:
            pages = [Image.open(io.BytesIO(await file.read()))]
        elif ext == ".pdf":
            pages = convert_from_bytes(await file.read())
        else:
            raise HTTPException(
                status_code=400, detail=f"{ext} Unsupported file type")

        for i, page in enumerate(pages):
            width, height = page.size
            # import pdb; pdb.set_trace()
            if max_height and int(height) > max_height:
                page = page.resize(
                    (int(width * max_height / height), max_height))

            if return_image:
                base64_images.append(image_to_base64(page))

            if grayscale:
                page = ImageOps.grayscale(page)

            page_list.append(page)
            page_ids.append(i)

        return dict(msg="success", results=ocr_model.perform_ocr(np.array(page)), status="200", images_base64=base64_images if base64_images else None, page_ids=page_ids)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/read")
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
