from src.schemas.box import Bbox
from src.schemas.output import OCRResult, Page


def test_set_text_with_two_pages_and_lines():
    # Page 1 with two lines
    page1_boxes = [
        Bbox(x=0.1, y=0.1, width=1, height=1, confidence=1, text="Hello"),
        Bbox(x=0.2, y=0.1, width=1, height=1, confidence=1, text="world"),
        Bbox(x=0.1, y=0.2, width=1, height=1, confidence=1, text="Line"),
        Bbox(x=0.2, y=0.2, width=1, height=1, confidence=1, text="two"),
    ]
    # Page 2 with one line
    page2_boxes = [
        Bbox(x=0.1, y=0.1, width=1, height=1, confidence=1, text="Second"),
        Bbox(x=0.2, y=0.1, width=1, height=1, confidence=1, text="page"),
    ]

    ocr = OCRResult(
        type="ocr",
        model_name="test-model",
        created_at=0,
        updated_at=0,
        version="1.0",
        total_pages=2,
        pages=[
            Page(page=1, boxes=page1_boxes),
            Page(page=2, boxes=page2_boxes),
        ],
    )

    ocr.set_text()

    # Assert that the text is structured properly
    expected_text = (
        "-------------------- Page: 1 --------------------\n"
        "Hello world\n"
        "Line two\n"
        "-------------------- Page: 2 --------------------\n"
        "Second page"
    )
    assert ocr.text.strip() == expected_text.strip()


def test_set_text_page():
    page1_boxes = [
        Bbox(x=0.1, y=0.1, width=1, height=1, confidence=1, text="Hello"),
        Bbox(x=0.2, y=0.1, width=1, height=1, confidence=1, text="world"),
        Bbox(x=0.1, y=0.2, width=1, height=1, confidence=1, text="Line"),
        Bbox(x=0.2, y=0.2, width=1, height=1, confidence=1, text="two"),
    ]
    # Page 2 with one line
    page2_boxes = [
        Bbox(x=0.1, y=0.1, width=1, height=1, confidence=1, text="Second"),
        Bbox(x=0.2, y=0.1, width=1, height=1, confidence=1, text="page"),
    ]

    ocr = OCRResult(
        type="ocr",
        model_name="test-model",
        created_at=0,
        updated_at=0,
        version="1.0",
        total_pages=2,
        pages=[
            Page(page=1, boxes=page1_boxes),
            Page(page=2, boxes=page2_boxes),
        ],
    )
    page1_text = ocr.set_page_text(ocr.pages[0])
    expected_page1_text = "Hello world\nLine two"
    assert page1_text.strip() == expected_page1_text.strip()
