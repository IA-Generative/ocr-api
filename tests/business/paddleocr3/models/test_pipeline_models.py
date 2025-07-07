import os
from PIL import Image
from pathlib import Path
from src.schemas.output import Page
from business.paddleocr3.models.pipeline import PipelineLinearPrediction
from business.paddleocr3.models.formula import PaddleFormulaRecognizer
from business.paddleocr3.models.layout import PaddleLayoutDetection
from business.paddleocr3.models.paddle import PaddleInferOCR
from src.utils.draw import (
    draw_normalized_layout,
    draw_normalized_bboxes,
    draw_normalized_checkboxes,
)
import json

DEVICE = os.environ.get("DEVICE", "cpu")


def test_pipeline_ocr():
    obj = PipelineLinearPrediction(
        models=[
            PaddleInferOCR(device=DEVICE),
            PaddleLayoutDetection(device=DEVICE),
            PaddleFormulaRecognizer(device=DEVICE),
        ]
    )
    path_image = Path("tests/data/valid/Exo7-algebre-page40.jpg")
    image = Image.open(path_image).convert("RGB")

    actual_pages = obj.batch_predict(images=[image])
    assert len(actual_pages) == 1
    assert isinstance(actual_pages[0], Page)
    assert len(actual_pages[0].layouts) != 0
    for layout in actual_pages[0].layouts:
        print(layout.label, layout.content)

    folder_image = Path("tests/data/predictions/valid/Exo7-algebre-page40/layouts")
    folder_image.mkdir(parents=True, exist_ok=True)

    result_image = draw_normalized_layout(image=image, layouts=actual_pages[0].layouts)
    w, h = result_image.size
    new_size = (w // 2, h // 2)

    result_image = result_image.resize(new_size, Image.Resampling.LANCZOS)

    result_image.save(folder_image / f"{path_image.stem}{path_image.suffix}")
    with open(folder_image / f"{path_image.stem}.json", "w") as f:
        json.dump([lay.model_dump() for lay in actual_pages[0].layouts], f, indent=2)

    folder_image = Path("tests/data/predictions/valid/Exo7-algebre-page40/bboxes")
    folder_image.mkdir(parents=True, exist_ok=True)
    result_image_bboxes = draw_normalized_bboxes(image, boxes=actual_pages[0].boxes)
    w, h = result_image_bboxes.size
    new_size = (w // 2, h // 2)

    result_image_bboxes = result_image_bboxes.resize(new_size, Image.Resampling.LANCZOS)

    result_image_bboxes.save(folder_image / f"{path_image.stem}{path_image.suffix}")


def test_pipeline_ocr_checkbox():
    from business.checkbox_service.models.box_detection import BoxDetection

    obj = PipelineLinearPrediction(
        models=[
            PaddleInferOCR(device=DEVICE, lang="en", ocr_version="PP-OCRv4"),
            PaddleLayoutDetection(device=DEVICE),
            PaddleFormulaRecognizer(device=DEVICE),
            BoxDetection(),
        ]
    )
    path_image = Path("tests/data/valid/formulaire-cerfa-complete.png")
    image = Image.open(path_image).convert("RGB")

    actual_pages = obj.batch_predict(images=[image])
    assert len(actual_pages) == 1
    assert isinstance(actual_pages[0], Page)
    assert len(actual_pages[0].layouts) != 0
    for layout in actual_pages[0].layouts:
        print(layout.label, layout.content)

    ####### Layouts #######
    folder_image = Path("tests/data/predictions/valid/formulaire-cerfa-complete/layouts")
    folder_image.mkdir(parents=True, exist_ok=True)

    result_image = draw_normalized_layout(image=image.copy(), width=5, layouts=actual_pages[0].layouts)

    w, h = result_image.size
    new_size = (w // 2, h // 2)

    result_image = result_image.resize(new_size, Image.Resampling.LANCZOS)

    result_image.save(folder_image / f"{path_image.stem}{path_image.suffix}")
    with open(folder_image / f"{path_image.stem}.json", "w") as f:
        json.dump([lay.model_dump() for lay in actual_pages[0].layouts], f, indent=2)

    ####### Layouts #######
    ####### BBoxes  #######

    folder_image = Path("tests/data/predictions/valid/formulaire-cerfa-complete/bboxes")
    folder_image.mkdir(parents=True, exist_ok=True)
    result_image_bboxes = draw_normalized_bboxes(image.copy(), boxes=actual_pages[0].boxes)
    w, h = result_image_bboxes.size
    new_size = (w // 2, h // 2)

    result_image_bboxes = result_image_bboxes.resize(new_size, Image.Resampling.LANCZOS)

    result_image_bboxes.save(folder_image / f"{path_image.stem}{path_image.suffix}")
    ####### BBoxes  #######

    ####### Checkboxes  #######
    folder_image = Path("tests/data/predictions/valid/formulaire-cerfa-complete/checkboxes")
    folder_image.mkdir(parents=True, exist_ok=True)
    result_image_bboxes = draw_normalized_checkboxes(image.copy(), checkboxes=actual_pages[0].checkboxes)
    w, h = result_image_bboxes.size
    new_size = (w // 2, h // 2)

    result_image_bboxes = result_image_bboxes.resize(new_size, Image.Resampling.LANCZOS)

    result_image_bboxes.save(folder_image / f"{path_image.stem}{path_image.suffix}")
