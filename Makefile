IMAGE_NAME_OCR_BACKEND=ocr-api
IMAGE_NAME_OCR_SERVICE=ocr-service
PYTHONPATH=$(PWD)

.PHONY: build test clean install-test install-test-dep linter tests build-images bump-patch donwload-model



install-test:
	curl -LsSf https://astral.sh/uv/install.sh | sh

install-test-dep: install-test
	apt-get update && apt-get install -y poppler-utils
	uv sync --group test --group ocr-backend --group ocr-service

donwload-model: install-test-dep
	export PYTHONPATH=$(PWD) && uv run ocr_service/utils/download.py

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

down-env:
	docker compose -f docker-compose-dev.yml down || true
	
tests: install-test-dep up-env donwload-model
	export PYTHONPATH=$(PWD) && env $(shell grep -v '^#' .env | xargs) uv run pytest --cov=./ocr_backend --cov=./ocr_service --cov=./src tests/

build-ocr-backend:
	docker build -t $(IMAGE_NAME_OCR_BACKEND) -f Dockerfiles/ocr_backend/Dockerfile .

build-ocr-service:
	docker build -t $(IMAGE_NAME_OCR_SERVICE) -f Dockerfiles/ocr_service/Dockerfile .


build-images: build-ocr-backend build-ocr-service

clean:
	rm -rf tmp || true
	# docker rmi $(IMAGE_NAME_OCR_BACKEND) || true
	# docker rmi $(IMAGE_NAME_OCR_SERVICE) || true
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	
