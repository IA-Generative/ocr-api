import zipfile

import pytest
from PIL import Image

from services.utils.lazy_zip import LazyZipList

PDF_PATH = "tests/data/valid/cerfa_13750-05-1.pdf"
IMAGE_PATH = "tests/data/valid/identite.jpg"


def _build_zip(tmp_path, names_to_paths: dict) -> str:
    zip_path = tmp_path / "archive.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for name, path in names_to_paths.items():
            zf.write(path, arcname=name)
    return str(zip_path)


@pytest.fixture
def pdf_and_image_zip(tmp_path) -> str:
    # Ordre d'insertion volontairement inverse de l'ordre alphabétique.
    return _build_zip(
        tmp_path,
        {
            "b_image.jpg": IMAGE_PATH,
            "a_document.pdf": PDF_PATH,
        },
    )


def test_load_image_converts_to_rgb():
    image = LazyZipList._load_image(IMAGE_PATH)

    assert isinstance(image, Image.Image)
    assert image.mode == "RGB"


def test_lazy_zip_list_extracts_entries_alphabetically(pdf_and_image_zip):
    lazy = LazyZipList(pdf_and_image_zip)

    assert [entry["filename"] for entry in lazy.entries] == [
        "a_document.pdf",
        "b_image.jpg",
    ]


def test_lazy_zip_list_len_and_pages(pdf_and_image_zip):
    lazy = LazyZipList(pdf_and_image_zip)
    pdf_pages = lazy.entries[0]["page_count"]

    assert pdf_pages > 0
    assert len(lazy) == pdf_pages + 1

    # Les pages du PDF (ordre alphabétique) précèdent la page de l'image.
    for i in range(pdf_pages):
        assert isinstance(lazy[i], Image.Image)
    image_page = lazy[pdf_pages]
    assert isinstance(image_page, Image.Image)
    assert image_page.size == Image.open(IMAGE_PATH).size


def test_lazy_zip_list_negative_index(pdf_and_image_zip):
    lazy = LazyZipList(pdf_and_image_zip)

    assert lazy[-1].size == lazy[len(lazy) - 1].size


def test_lazy_zip_list_slice_returns_list(pdf_and_image_zip):
    lazy = LazyZipList(pdf_and_image_zip)

    pages = lazy[0 : len(lazy)]
    assert isinstance(pages, list)
    assert len(pages) == len(lazy)
    assert all(isinstance(page, Image.Image) for page in pages)


def test_lazy_zip_list_index_out_of_range(pdf_and_image_zip):
    lazy = LazyZipList(pdf_and_image_zip)

    with pytest.raises(IndexError):
        lazy[len(lazy)]


def test_lazy_zip_list_invalid_index_type(pdf_and_image_zip):
    lazy = LazyZipList(pdf_and_image_zip)

    with pytest.raises(TypeError):
        lazy["0"]


def test_lazy_zip_list_page_sources_and_ocr_pages(pdf_and_image_zip):
    lazy = LazyZipList(pdf_and_image_zip)
    pdf_pages = lazy.entries[0]["page_count"]

    assert lazy.entries[0]["kind"] == "ocr"
    assert lazy.entries[1]["kind"] == "ocr"
    assert lazy.ocr_pages == set(range(pdf_pages + 1))
    assert all(source is None for source in lazy.page_sources)


def test_lazy_zip_list_skips_unrenderable_entry(tmp_path):
    corrupt_path = tmp_path / "broken.corrupt"
    corrupt_path.write_bytes(b"not a real document, just garbage bytes")

    zip_path = _build_zip(
        tmp_path,
        {
            "a_document.pdf": PDF_PATH,
            "z_broken.corrupt": str(corrupt_path),
        },
    )

    lazy = LazyZipList(zip_path)

    broken_entry = next(e for e in lazy.entries if e["filename"] == "z_broken.corrupt")
    assert broken_entry["kind"] == "skip"
    assert broken_entry["page_count"] == 0
    # Seule la page du PDF est comptée dans la séquence composite.
    assert len(lazy) == lazy.entries[0]["page_count"]


def test_lazy_zip_list_ignores_directory_entries(tmp_path):
    zip_path = tmp_path / "with_dir.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr(zipfile.ZipInfo("folder/"), "")
        zf.write(PDF_PATH, arcname="folder/a_document.pdf")

    lazy = LazyZipList(str(zip_path))

    assert [entry["filename"] for entry in lazy.entries] == ["folder/a_document.pdf"]


def test_lazy_zip_list_repr(pdf_and_image_zip):
    lazy = LazyZipList(pdf_and_image_zip)

    assert repr(lazy) == (f"<LazyZipList pages={len(lazy)} entries={len(lazy.entries)} zip='{pdf_and_image_zip}'>")
