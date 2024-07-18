import requests
import base64
import glob

for img_path in glob.glob("test_images/*"):
    with open(img_path, "rb") as image_file:
        encoded_data = base64.b64encode(image_file.read()).decode()

    res = requests.post(
                        url='http://localhost:5000/',
                        # url='https://mirai-ocr-api.cloud-pi-native.com/predict/ocr_system',
                        json={"images": [encoded_data]}).json()['results'][0]
    print("-------",len(res))
    print(res)
    print("\n\n")