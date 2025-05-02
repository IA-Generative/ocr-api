import json
import os
import shutil
import tempfile
import traceback
from typing import Union, Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pdf2image import convert_from_bytes
from PIL import Image

from src.logger import logger


router = APIRouter(tags=["Transformer"])


class ContentTypeError(Exception): ...


class Page(BaseModel):
    width: int
    height: int
    image: Union[str, bytes]
    fmt: str


class TransformedPdf(BaseModel):
    source: str
    content_type: str
    size: int
    nb_pages: int
    pages: List[Page]
    extras: Optional[dict] = None


# sudo apt-get install poppler-utils
@router.post("/pdf2images/", response_model=TransformedPdf)
async def pdf_2_images(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise ContentTypeError(f"{file.content_type} not supported")
    fmt = "jpeg"
    images: List[Image.Image] = convert_from_bytes(file.read(), fmt=fmt)
    pages: list[Page] = []
    for image in images:
        width, height = image.size
        im_bytes = image.getvalue()
        im_b64 = base64.b64encode(im_bytes)

        page = Page(width=width, height=height, image=im_b64, fmt=fmt)
        pages.append(page)
    return TransformedPdf(
        source=file.filename,
        content_type=file.content_type,
        size=file.size,
        nb_pages=len(page),
        pages=pages,
    )
