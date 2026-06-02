from liteparse.types import ParseResult
from typing import overload
from PIL import Image
from collections.abc import Sequence
from liteparse import LiteParse
from io import BytesIO


class LazyFileImageList(Sequence):
    """
    Liste paresseuse (lazy) d’images extraites d’un PDF. Chaque image est chargée à la demande.
    Se comporte comme une vraie liste : indexation, slicing, itération, len().
    """

    def __init__(self, file_path, dpi=200, fmt="jpeg"):
        self.file_path = file_path
        self.dpi = dpi
        self.fmt = fmt

        self.parser = LiteParse(
            ocr_enabled=False,  # Enable OCR (default: True)
            ocr_language="eng",  # Tesseract language code
            ocr_server_url=None,  # HTTP OCR server URL (optional)
            tessdata_path=None,  # Path to tessdata directory (optional)
            max_pages=None,  # Max pages to parse
            target_pages=None,  # Specific pages (optional)
            dpi=dpi,  # Rendering DPI
            preserve_very_small_text=False,  # Keep tiny text
            password=None,  # Password for protected documents
            quiet=False,  # Suppress progress output
            num_workers=1,  # Concurrent OCR workers
        )
        self.info: ParseResult = self.parser.parse(self.file_path)
        self._total_pages = len(self.info.pages)

    def __len__(self):
        return self._total_pages

    def bytes_to_image(self, page_bytes: bytes) -> Image.Image:

        image = Image.open(BytesIO(page_bytes))
        if image.mode != "RGB":
            image = image.convert("RGB")
        return image

    @overload
    def __getitem__(self, index: int) -> Image.Image: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[Image.Image]: ...

    def __getitem__(self, index: int | slice) -> Image.Image | Sequence[Image.Image]:
        if not isinstance(index, (int, slice)):
            raise TypeError("Index must be int or slice")
        if isinstance(index, slice):
            return [self[i] for i in range(*index.indices(len(self)))]

        if index < 0:
            index += len(self)
        if not (0 <= index < len(self)):
            raise IndexError("Page index out of range")
        return self._load_page(index)

    def _load_page(self, index: int) -> Image.Image:
        page = self.parser.screenshot(self.file_path, page_numbers=[index + 1])
        images = [self.bytes_to_image(page_bytes.image_bytes) for page_bytes in page]
        return images[0]  # PIL Image

    def __repr__(self):
        return f"<LazyPdfImageList pages={len(self)} path='{self.file_path}'>"
