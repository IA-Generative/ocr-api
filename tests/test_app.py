import pytest
from fastapi.testclient import TestClient
from main import app, ImageRequest
import requests
import base64
from pathlib import Path

client = TestClient(app)

test_path = Path(__file__).parent.absolute()

def test_home_route():
    response = client.get("/")
    assert response.status_code == 200
    assert response.text == "API endpoint for OCR"

def test_ocr_with_valid_image():
    # import pdb; pdb.set_trace()
    if len(list((test_path.glob("data/valid/*")))) < 1:
        raise FileNotFoundError("You must create a folder test_images and put some images in it to test the API !")

    for img_path in test_path.glob("data/valid/*"):
        with open(img_path, "rb") as image_file:
            files = {"file": (img_path.name, image_file, "multipart/form-data")}

            #encoded_data = base64.b64encode(image_file.read()).decode()

            res = client.post(
                                url='http://localhost:5000/',
                                # url='https://ocr.c99.cloud-pi-native.com/predict/ocr_system',
                                files=files,
                                # json={"images": [encoded_data]},
                                headers={'Authorization': 'Basic dXNlcl9vY3I6SlFWRDRxNThzMg=='}).json()
            print("-------", res['msg'])
            #print(res['results'])
            print("\n\n")
            # import pdb; pdb.set_trace()
            assert len(res['results']) > 0

def test_ocr_with_invalid_image():
    request_data = {"images": ["invalid_base64_string"]}

    response = client.post("/", json=request_data)
    # import pdb; pdb.set_trace()
    assert response.status_code == 500