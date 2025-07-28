docker build -t paddle3 -f Dockerfiles/ocr_service/Dockerfile.paddle .


```bash
docker run --name paddle --rm -it   --cpus="2.0"   --memory="4g"   --memory-swap="4g"   -v "$(pwd)/benchmark/paddle/3.0.1:/app/benchmark" -v "$(pwd)/tests/data/valid/:/app/data" paddle3 bash
```
