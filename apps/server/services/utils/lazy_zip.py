import mimetypes
import tempfile
import zipfile
from collections.abc import Sequence
from pathlib import Path
from typing import Callable, overload

from PIL import Image

from src.logger import logger
from business.extractions.models.libre_extraction import (
    ODT_CONTENT_TYPE,
    ODS_CONTENT_TYPE,
    ODP_CONTENT_TYPE,
)
from business.extractions.models.docx_extraction import DOCX_CONTENT_TYPE
from business.extractions.models.excel_extraction import EXCEL_CONTENT_TYPE
from business.extractions.models.csv_extraction import CSV_CONTENT_TYPE

from .lazy_file import LazyFileImageList
from .lazy_pdf import LazyPdfImageList

PDF_CONTENT_TYPE = "application/pdf"

# Formats dont le texte est déjà extrait par liteparse (aucun OCR nécessaire).
TEXT_CONTENT_TYPES = (
    ODT_CONTENT_TYPE + ODS_CONTENT_TYPE + ODP_CONTENT_TYPE + DOCX_CONTENT_TYPE + EXCEL_CONTENT_TYPE + CSV_CONTENT_TYPE
)


class LazyZipList(Sequence):
    """
    Liste paresseuse (lazy) d’images extraites des fichiers d’une archive
    ZIP, dans l’ordre alphabétique de leur nom (à l’image de
    ``LazyEmailList`` pour les pièces jointes d’un email).

    Chaque fichier de l’archive devient un ou plusieurs segments de pages,
    rendus via ``LazyPdfImageList`` (PDF), chargement direct (image) ou
    ``LazyFileImageList`` (bureautique). Les entrées non rendables sont
    ignorées. Les index sont continus entre les fichiers, dans l’ordre
    alphabétique.
    """

    def __init__(self, file_path, dpi=200, fmt="jpeg"):
        self.zip_path = file_path
        self.dpi = dpi
        self.fmt = fmt

        self.entries = self._extract_entries(file_path)
        self._build_entry_lists()
        self._build_segments()
        self._build_page_sources()

    # ------------------------------------------------------------------ #
    # Extraction des fichiers de l'archive
    # ------------------------------------------------------------------ #
    @staticmethod
    def _extract_entries(file_path) -> list[dict]:
        entries = []
        with zipfile.ZipFile(file_path) as zf:
            names = sorted(info.filename for info in zf.infolist() if not info.is_dir())
            for name in names:
                payload = zf.read(name)
                if not payload:
                    continue
                safe_name = Path(name).name
                suffix = Path(safe_name).suffix or ".bin"
                tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
                tmp.close()
                Path(tmp.name).write_bytes(payload)
                content_type = mimetypes.guess_type(safe_name)[0] or "application/octet-stream"
                entries.append(
                    {
                        "filename": name,
                        "content_type": content_type,
                        "size": len(payload),
                        "path": tmp.name,
                        "lazy": None,
                        "kind": "skip",
                        "page_count": 0,
                    }
                )
        return entries

    # ------------------------------------------------------------------ #
    # Construction des sous-listes paresseuses de chaque fichier
    # ------------------------------------------------------------------ #
    @staticmethod
    def _load_image(path: str) -> Image.Image:
        image = Image.open(path)
        if image.mode != "RGB":
            image = image.convert("RGB")
        return image

    def _build_entry_lists(self) -> None:
        for entry in self.entries:
            content_type = entry["content_type"]
            try:
                if content_type == PDF_CONTENT_TYPE:
                    # PDF : rendu image puis OCR.
                    entry["lazy"] = LazyPdfImageList(entry["path"], dpi=self.dpi, fmt=self.fmt)
                    entry["kind"] = "ocr"
                elif content_type.startswith("image/"):
                    # Image : OCR.
                    entry["lazy"] = [self._load_image(entry["path"])]
                    entry["kind"] = "ocr"
                else:
                    # Bureautique (ODT, DOCX, ...) : texte déjà extrait par liteparse.
                    entry["lazy"] = LazyFileImageList(entry["path"], dpi=self.dpi, fmt=self.fmt)
                    entry["kind"] = "text" if content_type in TEXT_CONTENT_TYPES else "ocr"
                entry["page_count"] = len(entry["lazy"])
            except Exception as exc:  # fichier non rendable
                logger.warning(
                    f"Impossible de rendre le fichier {entry['filename']} ({entry['content_type']}) de l'archive: {exc}"
                )
                entry["lazy"] = None
                entry["kind"] = "skip"
                entry["page_count"] = 0

    # ------------------------------------------------------------------ #
    # Construction de la séquence composite
    # ------------------------------------------------------------------ #
    def _build_segments(self) -> None:
        # Chaque segment : (page_count, accessor(local_index) -> Image)
        self._segments: list[tuple[int, Callable[[int], Image.Image]]] = []
        for entry in self.entries:
            lazy = entry["lazy"]
            if lazy is None or entry["page_count"] <= 0:
                continue
            self._segments.append((entry["page_count"], lambda i, s=lazy: s[i]))
        self._total = sum(count for count, _ in self._segments)

    def _build_page_sources(self) -> None:
        """
        Pour chaque page composite, mémorise sa source d'extraction :
          - une ``ParsedPage`` liteparse si le texte est déjà disponible
            (fichiers bureautiques) ;
          - ``None`` si la page doit être OCR-isée (PDF / image), son index
            global étant alors ajouté à ``self.ocr_pages``.
        """
        self.page_sources: list = []
        self.ocr_pages: set[int] = set()
        global_idx = 0
        for entry in self.entries:
            if entry["kind"] == "skip" or entry["page_count"] <= 0:
                continue
            if entry["kind"] == "text":
                parsed_pages = entry["lazy"].info.pages
                for offset in range(entry["page_count"]):
                    parsed = parsed_pages[offset] if offset < len(parsed_pages) else None
                    self.page_sources.append(parsed)
                    global_idx += 1
            else:  # ocr (PDF / image)
                for _ in range(entry["page_count"]):
                    self.page_sources.append(None)
                    self.ocr_pages.add(global_idx)
                    global_idx += 1

    # ------------------------------------------------------------------ #
    # Interface séquence composite
    # ------------------------------------------------------------------ #
    def __len__(self) -> int:
        return self._total

    @overload
    def __getitem__(self, index: int) -> Image.Image: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[Image.Image]: ...

    def __getitem__(self, index: int | slice) -> Image.Image | Sequence[Image.Image]:
        if isinstance(index, slice):
            return [self[i] for i in range(*index.indices(len(self)))]
        if not isinstance(index, int):
            raise TypeError("Index must be int or slice")
        if index < 0:
            index += len(self)
        if not (0 <= index < len(self)):
            raise IndexError("Page index out of range")

        for count, accessor in self._segments:
            if index < count:
                return accessor(index)
            index -= count
        raise IndexError("Page index out of range")

    def __repr__(self):
        return f"<LazyZipList pages={len(self)} entries={len(self.entries)} zip='{self.zip_path}'>"
