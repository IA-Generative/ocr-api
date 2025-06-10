from pathlib import Path
from PIL import Image
from ocr_service.models.paddle_ocr import PaddleInferOCR
from src.schemas.output import Page
from src.utils.draw import draw_normalized_bboxes


def test_predict():
    obj = PaddleInferOCR()
    folder_output = Path("tests/data/predictions/valid/ocrv5")
    folder_output.mkdir(parents=True, exist_ok=True)

    #### Cerfa ####
    cerfa_path = Path("tests/data/valid/formulaire-cerfa-complete.png")
    image = Image.open(cerfa_path)
    images = [image]

    actuals = obj.batch_predict(images=images)

    assert len(actuals) == 1
    for actual in actuals:
        assert isinstance(actual, Page)

    pages: list[Page] = actuals
    for page, image in zip(pages, images):
        annotated = image.copy()
        annotated = draw_normalized_bboxes(image, page.boxes)
        out_path = folder_output / f"{cerfa_path.stem}{cerfa_path.suffix}"
        annotated.save(out_path)

    #### Copie bac ####
    bac_copy_path = Path("tests/data/valid/handwritten/copie-bac-2021-2.jpg")
    image = Image.open(bac_copy_path)
    images = [image]
    actuals = obj.batch_predict(images=images)
    pages: list[Page] = actuals
    for page, image in zip(pages, images):
        annotated = image.copy()
        annotated = draw_normalized_bboxes(image, page.boxes)
        out_path = folder_output / f"{bac_copy_path.stem}{bac_copy_path.suffix}"
        annotated.save(out_path)

    #### ID card ####
    bac_copy_path = Path("tests/data/valid/identite.jpg")
    image = Image.open(bac_copy_path)
    images = [image]
    actuals = obj.batch_predict(images=images)
    pages: list[Page] = actuals
    for page, image in zip(pages, images):
        annotated = image.copy()
        annotated = draw_normalized_bboxes(image, page.boxes)
        out_path = folder_output / f"{bac_copy_path.stem}{bac_copy_path.suffix}"
        annotated.save(out_path)

    #### Formula ####
    bac_copy_path = Path("tests/data/valid/general_formula_rec_001_res_paddleocr3.png")
    image = Image.open(bac_copy_path)
    images = [image]
    actuals = obj.batch_predict(images=images)
    pages: list[Page] = actuals
    for page, image in zip(pages, images):
        annotated = image.copy()
        annotated = draw_normalized_bboxes(image, page.boxes)
        out_path = folder_output / f"{bac_copy_path.stem}{bac_copy_path.suffix}"
        annotated.save(out_path)

    # https://i.pinimg.com/736x/88/be/1a/88be1a85beb4b2167fa00e352d6b5519.jpg
    bac_copy_path = Path("tests/data/valid/handwritten/franc-copie.jpg")
    image = Image.open(bac_copy_path)
    images = [image]
    actuals = obj.batch_predict(images=images)
    pages: list[Page] = actuals
    for page, image in zip(pages, images):
        annotated = image.copy()
        annotated = draw_normalized_bboxes(image, page.boxes)
        out_path = folder_output / f"{bac_copy_path.stem}{bac_copy_path.suffix}"
        annotated.save(out_path)

    # https://www.revmed.ch/var/site/storage/images/7/8/5/8/6958587-1-fre-CH/pg416-1_i1200.jpg

    tableau_path = Path("tests/data/valid/tebleau/tableau-climatique.jpg")
    image = Image.open(tableau_path)
    images = [image]
    actuals = obj.batch_predict(images=images)
    pages: list[Page] = actuals
    for page, image in zip(pages, images):
        annotated = image.copy()
        annotated = draw_normalized_bboxes(image, page.boxes)
        out_path = folder_output / f"{tableau_path.stem}{tableau_path.suffix}"
        annotated.save(out_path)

    # https://upload.wikimedia.org/wikipedia/commons/4/47/C_tableau_climatique_qui_provient_d%27une_page_Wikip%C3%A9dia_francophone_18_f%C3%A9vrier_2014.jpg

    tableau_path = Path(
        "tests/data/valid/tebleau/C_tableau_climatique_qui_provient_d'une_page_Wikipédia_francophone_18_février_2014.jpg"
    )
    image = Image.open(tableau_path)
    images = [image]
    actuals = obj.batch_predict(images=images)
    pages: list[Page] = actuals
    for page, image in zip(pages, images):
        annotated = image.copy()
        annotated = draw_normalized_bboxes(image, page.boxes)
        out_path = folder_output / f"{tableau_path.stem}{tableau_path.suffix}"
        annotated.save(out_path)


def test_load_dataset():
    from datasets import load_dataset
    # from pdf2image import convert_from_bytes

    ds = load_dataset("opendatalab/OmniDocBench", split="train", streaming=True)
    print(ds.features)
    print(79 * "*")

    # for item in ds:
    #     print(item)
    #     if item.get("language") != "en":
    #         continue
    #     fn = item["file_name"]
    #     print("Processing:", fn)
    #     # pdf_bytes = item["file"].read()
    #     # pil_images = convert_from_bytes(pdf_bytes, dpi=200)

    #     # for page_i, img in enumerate(pil_images):
    #     #     img_path = f"{fn}_page{page_i+1}.png"
    #     #     print(img_path)
