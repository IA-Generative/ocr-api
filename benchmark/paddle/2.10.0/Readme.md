# Stats

```bash
docker build -t paddle -f Dockerfiles/ocr_service/Dockerfile.2.10.0.paddle .
```

```bash
docker run --name paddle --rm -it   --cpus="2.0"   --memory="4g"   --memory-swap="4g"   -v "$(pwd)/benchmark/paddle/2.10.0:/app/benchmark" -v "$(pwd)/tests/data/valid/:/app/data"   paddle bash
```

avg time :

- `/app/data/formulaire-cerfa-complete.png` - process in `3.9s`.
