from PIL import Image
from ocr_service.utils.image import image_to_base64


def test_image_tob64():
    image = Image.open("tests/data/valid/formulaire-cerfa-complete.png")
    actual = image_to_base64(image=image, format='PNG')
    assert isinstance(actual, str)
