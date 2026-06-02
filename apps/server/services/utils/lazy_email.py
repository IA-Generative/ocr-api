import re
import tempfile
from collections.abc import Sequence
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from pathlib import Path
from typing import Callable, overload

from PIL import Image

from odf.opendocument import OpenDocumentText
from odf.style import Style, TextProperties
from odf.text import H, P

from src.logger import logger

from .lazy_file import LazyFileImageList
from .lazy_pdf import LazyPdfImageList

PDF_CONTENT_TYPE = "application/pdf"


class LazyEmailList(LazyFileImageList):
    """
    Liste paresseuse (lazy) d’images extraites d’un email (.eml).

    La séquence est composite :
      - elle commence par la (ou les) page(s) de l’email lui-même
        (métadonnées, corps, et table des pièces jointes avec la page de
        début de chacune) ;
      - puis viennent les pages de chaque pièce jointe, rendues via
        ``LazyPdfImageList`` (PDF) ou ``LazyFileImageList`` (autres formats).

    Les index sont continus : ils enchaînent la page de l’email puis les
    pages des pièces jointes, dans l’ordre.
    """

    def __init__(self, file_path, dpi=200, fmt="jpeg"):
        self.email_path = file_path
        self.dpi = dpi
        self.fmt = fmt

        # 1. Parse de l'email et extraction de son contenu
        message = self._parse_email(file_path)
        self.metadata = self._extract_metadata(message)
        self.body = self._extract_body(message)
        self.attachments = self._extract_attachments(message)

        # 2. Construction des sous-listes (lazy) pour chaque pièce jointe
        self._build_attachment_lists()

        # 3. Première génération de la page ODT pour connaître le nombre de
        #    pages occupées par l'email lui-même.
        odt_path = self._build_odt()
        super().__init__(odt_path, dpi=dpi, fmt=fmt)
        email_pages = self._total_pages

        # 4. Calcul des pages de début de chaque pièce jointe, puis
        #    régénération de l'ODT avec ces indications (table des matières).
        self._compute_attachment_start_pages(email_pages)
        odt_path = self._build_odt()
        super().__init__(odt_path, dpi=dpi, fmt=fmt)

        # 5. Construction de la séquence composite (email + pièces jointes)
        self._build_segments(self._total_pages)

    # ------------------------------------------------------------------ #
    # Extraction du contenu de l'email
    # ------------------------------------------------------------------ #
    @staticmethod
    def _parse_email(file_path) -> EmailMessage:
        with open(file_path, "rb") as f:
            return BytesParser(policy=policy.default).parse(f)

    @staticmethod
    def _extract_metadata(message: EmailMessage) -> dict:
        return {
            "Sujet": message["Subject"],
            "De": message["From"],
            "À": message["To"],
            "Cc": message["Cc"],
            "Cci": message["Bcc"],
            "Date": message["Date"],
            "Message-ID": message["Message-ID"],
        }

    @staticmethod
    def _extract_body(message: EmailMessage) -> str:
        """Retourne le corps texte (préfère text/plain, sinon text/html)."""
        body_part = message.get_body(preferencelist=("plain", "html"))
        if body_part is None:
            return ""
        content = body_part.get_content()
        if body_part.get_content_type() == "text/html":
            content = re.sub(r"<[^>]+>", "", content)
        return content.strip()

    def _extract_attachments(self, message: EmailMessage) -> list[dict]:
        attachments = []
        for index, part in enumerate(message.walk()):
            disposition = part.get_content_disposition()
            filename = part.get_filename()
            if disposition != "attachment" and not filename:
                continue
            payload = part.get_payload(decode=True)
            if not isinstance(payload, bytes) or not payload:
                continue
            safe_name = Path(filename or f"attachment_{index}").name
            suffix = Path(safe_name).suffix or ".bin"
            tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
            tmp.close()
            Path(tmp.name).write_bytes(payload)
            attachments.append(
                {
                    "filename": safe_name,
                    "content_type": part.get_content_type(),
                    "size": len(payload),
                    "path": tmp.name,
                    "lazy": None,
                    "page_count": 0,
                    "start_page": None,
                }
            )
        return attachments

    # ------------------------------------------------------------------ #
    # Construction des sous-listes paresseuses des pièces jointes
    # ------------------------------------------------------------------ #
    def _build_attachment_lists(self) -> None:
        for att in self.attachments:
            try:
                if att["content_type"] == PDF_CONTENT_TYPE:
                    lazy = LazyPdfImageList(att["path"], dpi=self.dpi, fmt=self.fmt)
                else:
                    lazy = LazyFileImageList(att["path"], dpi=self.dpi, fmt=self.fmt)
                att["lazy"] = lazy
                att["page_count"] = len(lazy)
            except Exception as exc:  # pièce jointe non rendable (zip, etc.)
                logger.warning(
                    "Impossible de rendre la pièce jointe {} ({}): {}",
                    att["filename"],
                    att["content_type"],
                    exc,
                )
                att["lazy"] = None
                att["page_count"] = 0

    def _compute_attachment_start_pages(self, email_pages: int) -> None:
        # Pages affichées en base 1 ; l'email occupe les pages 1..email_pages.
        offset = email_pages
        for att in self.attachments:
            if att["page_count"] > 0:
                att["start_page"] = offset + 1
                offset += att["page_count"]
            else:
                att["start_page"] = None

    # ------------------------------------------------------------------ #
    # Construction de la séquence composite
    # ------------------------------------------------------------------ #
    def _build_segments(self, email_pages: int) -> None:
        # Chaque segment : (page_count, accessor(local_index) -> Image)
        self._segments: list[tuple[int, Callable[[int], Image.Image]]] = [
            (email_pages, lambda i: LazyFileImageList._load_page(self, i))
        ]
        for att in self.attachments:
            lazy = att["lazy"]
            if lazy is None or att["page_count"] <= 0:
                continue
            self._segments.append((att["page_count"], lambda i, s=lazy: s[i]))
        self._total = sum(count for count, _ in self._segments)

    # ------------------------------------------------------------------ #
    # Génération de la page ODT
    # ------------------------------------------------------------------ #
    @staticmethod
    def _attachment_line(att: dict) -> str:
        if att.get("start_page"):
            location = f"commence page {att['start_page']}"
        elif att["page_count"] <= 0:
            location = "non rendable"
        else:
            location = "à la suite"
        return (
            f"- {att['filename']} "
            f"({att['content_type']}, {att['size']} octets) — {location}"
        )

    def _build_odt(self) -> str:
        doc = OpenDocumentText()

        bold = Style(name="Bold", family="text")
        bold.addElement(TextProperties(fontweight="bold"))
        doc.styles.addElement(bold)

        # Métadonnées
        doc.text.addElement(H(outlinelevel=1, text="Métadonnées de l'email"))
        for label, value in self.metadata.items():
            p = P()
            p.addText(f"{label} : {value if value else ''}")
            doc.text.addElement(p)

        # Corps
        doc.text.addElement(H(outlinelevel=1, text="Contenu de l'email"))
        if self.body:
            for line in self.body.splitlines():
                doc.text.addElement(P(text=line))
        else:
            doc.text.addElement(P(text="(corps vide)"))

        # Pièces jointes (avec page de début quand connue)
        doc.text.addElement(H(outlinelevel=1, text="Pièces jointes"))
        if not self.attachments:
            doc.text.addElement(P(text="Aucune pièce jointe."))
        else:
            for att in self.attachments:
                doc.text.addElement(P(text=self._attachment_line(att)))

        tmp = tempfile.NamedTemporaryFile(suffix=".odt", delete=False)
        tmp.close()
        doc.save(tmp.name)
        return tmp.name

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
        return (
            f"<LazyEmailList pages={len(self)} "
            f"attachments={len(self.attachments)} email='{self.email_path}'>"
        )
