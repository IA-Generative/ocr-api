import pytest
from fastapi.testclient import TestClient
from main import app
import requests
import base64
from pathlib import Path

client = TestClient(app)

test_path = Path(__file__).parent.absolute()

def test_home_route():
    response = client.get("/")
    #assert response.status_code == 200
    assert response.text == "API endpoint for OCR"

def test_ocr_with_valid_image():
    # import pdb; pdb.set_trace()
    if len(list((test_path.glob("data/valid/*")))) < 1:
        raise FileNotFoundError("You must create a folder test_images and put some images in it to test the API !")

    for img_path in test_path.glob("data/valid/*"):
        with open(img_path, "rb") as image_file:
            files = {"file": (img_path.name, image_file, "multipart/form-data")}

            res = client.post(url='http://localhost:5000/?max_height=200&grayscale=true',
                            # url='https://ocr.c99.cloud-pi-native.com/predict/ocr_system',
                            files=files).json()
            print("\n\n")
            assert len(res['results']) > 0
            if img_path.suffix == ".pdf":
                # check if there is several pages
                #import pdb; pdb.set_trace()
                assert True


def test_ocr_with_invalid_image():
    request_data = {"images": ["invalid_base64_string"]}

    response = client.post("/", json=request_data)
    # import pdb; pdb.set_trace()
    assert response.status_code == 422


def test_read():
    ocr_data = [
            [
                {'confidence': 0.9941, 'text': 'cerfa', 'text_region': [[1450, 105], [1558, 105], [1558, 149], [1450, 149]]},
                {'confidence': 0.985, 'text': 'form', 'text_region': [[1600, 105], [1700, 105], [1700, 149], [1600, 149]]}
            ],
            [
                {'confidence': 0.992, 'text': 'page', 'text_region': [[100, 100], [200, 100], [200, 150], [100, 150]]},
                {'confidence': 0.990, 'text': 'two', 'text_region': [[210, 100], [300, 100], [300, 150], [210, 150]]}
            ]
        ]
    response = client.post(url="http://localhost:5000/read/", json=ocr_data)
    assert response.status_code == 200
    assert response.json() == 'cerfa form\n\npage two\n\n'
