# ocr-api
API endoint for testing OCR

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