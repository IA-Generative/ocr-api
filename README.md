# ocr-api
API endpoint for testing OCR

## Install

```bash
# with pip
pip install -r requirements.txt^

# with docker
docker build -t ocr-api .
```

## Run
```bash
# with python
uvicorn main:app --reload --host 0.0.0.0 --port 5000

# with docker
docker run --rm -p 5000:5000 -v $PWD:/app ocr-api
```

then open `localhost:5000`

## Test
Use file `test.py` or write some code:
```python
import requests
import base64


with open("image_test.jpg", "rb") as image_file:
    encoded_data = base64.b64encode(image_file.read()).decode()

res = requests.post(
                    url='http://localhost:5000/',
                    json={"images": [encoded_data]}).json()
print("-------",res['msg'])
print(res['results'])
print("\n\n")
```
