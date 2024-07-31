import requests
import base64
import glob

if len(glob.glob("tests/data/*")) < 1:
    raise FileNotFoundError("You must create a folder test_images and put some images in it to test the API !")

for img_path in glob.glob("tests/data/*"):
    with open(img_path, "rb") as image_file:
        encoded_data = base64.b64encode(image_file.read()).decode()

    res = requests.post(
                        url='http://localhost:5000/',
                        # url='https://ocr.c99.cloud-pi-native.com/predict/ocr_system',
                        json={"images": [encoded_data]},
                        headers={'Authorization': 'Basic dXNlcl9vY3I6SlFWRDRxNThzMg=='}).json()
    print("-------",res['msg'])
    print(res['results'])
    print("\n\n")