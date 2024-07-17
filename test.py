import requests
import base64

with open("image_test.jpg", "rb") as image_file:
    encoded_data = base64.b64encode(image_file.read()).decode()

res = requests.post(url='http://localhost:5000/',
                    json={"image": encoded_data})
print(res.json())