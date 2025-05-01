IMAGE_NAME_OCR_BACKEND=ocr-api
IMAGE_NAME_OCR_SERVICE=ocr-service
PYTHONPATH=$(PWD)

.PHONY: build test install-test install-test-dep linter tests build-images bump-patch donwload-model


install-uv:
	curl -LsSf https://astral.sh/uv/install.sh | sh

install-local: install-uv
ifeq ($(shell uname), Linux)
	sudo apt-get update && sudo apt-get install -y poppler-utils
else ifeq ($(shell uname), Darwin)
	brew install poppler
else
	@echo "Installation automatique non supportée sur cette plateforme"
endif
	uv sync --group test --group ocr-backend --group ocr-service --group ocr-service-paddle

linter: install-local
	uv run ruff check .

bump-patch: install-test
	uv run cz bump --increment patch

bump-minor: install-test
	uv run cz bump --increment minor

up:
	docker compose up -d

down:
	docker compose down || true

tests: up
	docker exec ocr-api pytest --cov=./ocr_backend --cov=./src --cov-report=term-missing tests/ocr_backend tests/src/
	docker exec ocr-service pytest --cov=./ocr_service tests/ocr_service

build-ocr-backend:
	docker compose build ocr_backend

build-ocr-service:
	docker compose build ocr_service

build-images: build-ocr-backend build-ocr-service

upgrade-db:
	docker exec ocr-api alembic upgrade head

upgrade-revision:
	docker exec ocr-api alembic revision --autogenerate

cluster:
	kind create cluster --name ocr --config ./kind/config.yaml
