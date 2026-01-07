from business.paddleocr2.models.markdown import PPStructureInferV5
from PIL import Image
from src.schemas.output import Page
import os


def test_ppstructure_infer_v5_initialization():
    PPStructureInferV5()


def test_ocr_inference():
    obj = PPStructureInferV5(
        use_chart_recognition=True,
        use_formula_recognition=True,
        use_region_detection=True,
        use_seal_recognition=False,
        use_doc_unwarping=True,
        use_doc_orientation_classify=True,
        use_textline_orientation=True,
    )

    image_path1 = "tests/data/valid/formulaire-cerfa-complete.png"
    image_path2 = "tests/data/valid/identite.jpg"
    image_path3 = "tests/data/valid/tableau.png"
    for image_path in [image_path1, image_path2, image_path3]:
        image = Image.open(image_path).convert("RGB")
        base_name = os.path.basename(image_path)
        actual_pages = obj.batch_predict(
            images=[image],
            save_markdown=f"tests/data/predictions/structure/{base_name}",
            save_visualization=f"tests/data/predictions/structure/{base_name}",
        )
        assert len(actual_pages) == 1
        assert isinstance(actual_pages[0], Page)
        assert actual_pages[0].markdown
