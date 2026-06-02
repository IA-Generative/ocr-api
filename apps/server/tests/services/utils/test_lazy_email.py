from PIL import Image

from services.utils.lazy_email import LazyEmailList

EML_PATH = "tests/data/valid/test-integration.eml"


def test_lazy_email_extracts_metadata_and_body():
    emails = LazyEmailList(EML_PATH)

    assert emails.metadata["Sujet"]
    assert emails.metadata["De"]
    assert emails.body  # le corps de l'email n'est pas vide


def test_lazy_email_lists_attachment():
    emails = LazyEmailList(EML_PATH)

    assert len(emails.attachments) == 1
    att = emails.attachments[0]
    assert att["filename"].endswith(".odt")
    assert att["page_count"] == 3


def test_lazy_email_composite_length_and_start_page():
    emails = LazyEmailList(EML_PATH)

    att = emails.attachments[0]
    email_pages = len(emails) - att["page_count"]

    assert email_pages >= 1
    # la pièce jointe commence juste après les pages de l'email (base 1)
    assert att["start_page"] == email_pages + 1
    # longueur totale = pages de l'email + pages de la pièce jointe
    assert len(emails) == email_pages + 3


def test_lazy_email_indexing_returns_images():
    emails = LazyEmailList(EML_PATH)

    first = emails[0]
    last = emails[len(emails) - 1]

    assert isinstance(first, Image.Image)
    assert isinstance(last, Image.Image)
    assert first.mode == "RGB"


def test_lazy_email_slicing_returns_all_pages():
    emails = LazyEmailList(EML_PATH)

    pages = emails[:]

    assert len(pages) == len(emails)
    assert all(isinstance(page, Image.Image) for page in pages)
