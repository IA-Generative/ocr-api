IMAGE_NAME_OCR_BACKEND=ocr-api
IMAGE_NAME_OCR_SERVICE=ocr-service
PYTHONPATH=$(PWD)

.PHONY: build test clean install-test install-test-dep linter tests build-images bump-patch



install-test:
	curl -LsSf https://astral.sh/uv/install.sh | sh

install-test-dep: install-test
	uv sync --group test --group ocr-backend 

linter: install-test-dep
	uv run ruff check .

bump-patch: install-test
	uv run cz bump --increment patch

bump-minor: install-test
	uv run cz bump --increment minor

up-env:
	docker compose -f docker-compose-dev.yml up -d
	@echo "Attente de 5 secondes pour laisser les conteneurs démarrer..."
	sleep 5
	
tests: install-test-dep up-env
	export PYTHONPATH=$(PWD) && env $(shell grep -v '^#' .env | xargs) uv run pytest tests/

build-ocr-backend:
	docker build -t $(IMAGE_NAME_OCR_BACKEND) -f Dockerfiles/ocr_backend/Dockerfile .

build-ocr-service:
	docker build -t $(IMAGE_NAME_OCR_SERVICE) -f Dockerfiles/ocr_backend/Dockerfile .


build-images: build-ocr-backend build-ocr-service

clean:
	rm -rf tmp || true
	# docker rmi $(IMAGE_NAME_OCR_BACKEND) || true
	# docker rmi $(IMAGE_NAME_OCR_SERVICE) || true
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	
