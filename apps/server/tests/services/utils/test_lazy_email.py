import zipfile
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser

import pytest
from PIL import Image

from services.utils.lazy_email import LazyEmailList

EML_PATH = "tests/data/test-integration.eml"
PDF_PATH = "tests/data/valid/cerfa_13750-05-1.pdf"
IMAGE_PATH = "tests/data/valid/identite.jpg"


def _parse(path: str) -> EmailMessage:
    with open(path, "rb") as f:
        return BytesParser(policy=policy.default).parse(f)


def _build_eml_with_zip_attachment(tmp_path) -> str:
    zip_path = tmp_path / "archive.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.write(PDF_PATH, arcname="a_document.pdf")
        zf.write(IMAGE_PATH, arcname="b_image.jpg")

    msg = EmailMessage()
    msg["Subject"] = "Archive de test"
    msg["From"] = "sender@example.com"
    msg["To"] = "receiver@example.com"
    msg.set_content("Voici une archive en pièce jointe.")
    msg.add_attachment(
        zip_path.read_bytes(),
        maintype="application",
        subtype="zip",
        filename="archive.zip",
    )

    eml_path = tmp_path / "with_zip.eml"
    eml_path.write_bytes(bytes(msg))
    return str(eml_path)


# ---------------------------------------------------------------------- #
# Parsing (métadonnées, corps, pièces jointes) — pas de rendu, pas besoin
# de LibreOffice.
# ---------------------------------------------------------------------- #
def test_parse_email_metadata():
    message = LazyEmailList._parse_email(EML_PATH)
    metadata = LazyEmailList._extract_metadata(message)

    assert metadata["Sujet"] == "test-integration"
    assert metadata["De"] == "test <test@interieur.gouv.fr>"
    assert metadata["À"] == "test@gmail.com"


def test_extract_body_returns_plain_text():
    message = LazyEmailList._parse_email(EML_PATH)
    body = LazyEmailList._extract_body(message)

    assert "Bonjour" in body


def test_extract_attachments_from_eml():
    message = LazyEmailList._parse_email(EML_PATH)
    lazy = LazyEmailList.__new__(LazyEmailList)
    attachments = lazy._extract_attachments(message)

    assert len(attachments) == 1
    assert attachments[0]["filename"] == "fullstack-detailler.odt"
    assert attachments[0]["content_type"] == "application/vnd.oasis.opendocument.text"
    assert attachments[0]["size"] > 0


# ---------------------------------------------------------------------- #
# Dispatch des pièces jointes (PDF / image / ZIP / bureautique) — rendu
# réel des sous-listes, sans dépendre du rendu ODT de l'email lui-même.
# ---------------------------------------------------------------------- #
def test_build_attachment_lists_zip_is_unfolded(tmp_path):
    eml_path = _build_eml_with_zip_attachment(tmp_path)
    message = LazyEmailList._parse_email(eml_path)

    lazy = LazyEmailList.__new__(LazyEmailList)
    lazy.dpi = 200
    lazy.fmt = "jpeg"
    lazy.attachments = lazy._extract_attachments(message)
    lazy._build_attachment_lists()

    assert len(lazy.attachments) == 1
    att = lazy.attachments[0]
    assert att["kind"] == "zip"
    assert att["page_count"] > 0
    assert att["lazy"].entries[0]["filename"] == "a_document.pdf"
    assert att["lazy"].entries[1]["filename"] == "b_image.jpg"


def test_append_attachment_sources_zip_propagates_ocr_pages(tmp_path):
    eml_path = _build_eml_with_zip_attachment(tmp_path)
    message = LazyEmailList._parse_email(eml_path)

    lazy = LazyEmailList.__new__(LazyEmailList)
    lazy.dpi = 200
    lazy.fmt = "jpeg"
    lazy.attachments = lazy._extract_attachments(message)
    lazy._build_attachment_lists()
    lazy.page_sources = []
    lazy.ocr_pages = set()

    att = lazy.attachments[0]
    global_idx = lazy._append_attachment_sources(att, 0)

    assert global_idx == att["page_count"]
    assert lazy.ocr_pages == set(range(att["page_count"]))
    assert len(lazy.page_sources) == att["page_count"]


def test_build_attachment_lists_skips_corrupt_zip(tmp_path):
    corrupt_zip = tmp_path / "broken.zip"
    corrupt_zip.write_bytes(b"not a real zip archive")

    msg = EmailMessage()
    msg["Subject"] = "Zip cassé"
    msg["From"] = "sender@example.com"
    msg["To"] = "receiver@example.com"
    msg.set_content("Corps")
    msg.add_attachment(
        corrupt_zip.read_bytes(),
        maintype="application",
        subtype="zip",
        filename="broken.zip",
    )
    eml_path = tmp_path / "broken.eml"
    eml_path.write_bytes(bytes(msg))

    message = LazyEmailList._parse_email(str(eml_path))
    lazy = LazyEmailList.__new__(LazyEmailList)
    lazy.dpi = 200
    lazy.fmt = "jpeg"
    lazy.attachments = lazy._extract_attachments(message)
    lazy._build_attachment_lists()

    att = lazy.attachments[0]
    assert att["kind"] == "skip"
    assert att["page_count"] == 0


# ---------------------------------------------------------------------- #
# Pipeline complet — nécessite LibreOffice (rendu de la page ODT de
# l'email) pour tourner de bout en bout.
# ---------------------------------------------------------------------- #
def test_lazy_email_list_full_pipeline():
    lazy = LazyEmailList(EML_PATH)

    assert len(lazy) > 0
    assert isinstance(lazy[0], Image.Image)
    assert lazy.attachments[0]["kind"] == "text"


def test_lazy_email_list_with_zip_attachment_full_pipeline(tmp_path):
    eml_path = _build_eml_with_zip_attachment(tmp_path)

    lazy = LazyEmailList(eml_path)

    att = lazy.attachments[0]
    assert att["kind"] == "zip"
    assert len(lazy) == lazy._total_pages + att["page_count"]
    assert isinstance(lazy[len(lazy) - 1], Image.Image)


def test_lazy_email_list_index_out_of_range():
    lazy = LazyEmailList(EML_PATH)

    with pytest.raises(IndexError):
        lazy[len(lazy)]


def test_lazy_email_list_repr():
    lazy = LazyEmailList(EML_PATH)

    assert repr(lazy) == (f"<LazyEmailList pages={len(lazy)} attachments={len(lazy.attachments)} email='{EML_PATH}'>")
