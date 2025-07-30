IMAGE_NAME_OCR_BACKEND=ocr-api
IMAGE_NAME_OCR_SERVICE=ocr-service
PYTHONPATH=$(PWD)
OCR_BACKEND_CONTAINER=ocr-api
OCR_FRONTEND_CONTAINER=ocr-frontend
STRESS_HOST=http://localhost:5000
HAS_GPU := $(shell nvidia-smi > /dev/null 2>&1 && echo yes || echo no)

.PHONY: install-uv install-local linter bump-patch bump-minor \
        up down tests build-ocr-backend build-ocr-service build \
        upgrade-db upgrade-revision cluster help

.DEFAULT_GOAL := help

help:
	@echo "Usage: make <command>"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}'

install: install-uv ## Installation de l'environnement pour du développement local (gestionnaire de dépendances)
	@if [ ! -d ".venv" ]; then \
		echo "Synchronisation des dépendances..."; \
		uv sync --group test --group ocr-backend --group ocr-service --group ocr-service-paddle; \
	else \
		echo "Dépendances déjà synchronisées (suppose .venv existant)"; \
	fi

install-uv:
	@if ! command -v uv >/dev/null 2>&1; then \
		echo "uv non trouvé, installation..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	else \
		echo "uv déjà installé"; \
	fi

install-linux:
	sudo apt update && sudo apt install -y poppler-utils

install-mac:
	brew install poppler

install-local: ## Installation des dépendances systèmes
ifeq ($(shell uname), Linux)
	@$(MAKE) install-linux
else ifeq ($(shell uname), Darwin)
	@$(MAKE) install-mac
else
	@echo "Installation automatique non supportée sur cette plateforme"
endif

lint: install-uv ## Lint le code du dépôt
	uv tool install ruff
	uv run ruff check .

bump:
	@echo "Usage: make bump-patch OR make bump-minor"

bump-patch:
	uv run cz bump --increment patch

bump-minor:
	uv run cz bump --increment minor

up: ## Lance l'environnement de développement en conteneurs
	docker compose up -d

up-frontend: ## Lance l'environnement frontend en conteneur
	docker compose -f docker-compose.vue.yaml up -d ocr_frontend

down: ## Eteint l'environnement de développement en conteneurs
	docker compose down || true

down-test:
	docker compose -f docker-compose-test.yaml down || true

down-frontend: ## Eteint l'environnement frontend en conteneur
	docker compose -f docker-compose.vue.yaml down || true

logs-api: ## Affiche les logs du conteneur de l'API
	docker compose logs -f $(OCR_BACKEND_CONTAINER)

logs-service: ## Affiche les logs du conteneur de service
	docker compose logs -f $(OCR_SERVICE_CONTAINER)

logs-frontend: ## Affiche les logs du conteneur de frontend
	docker compose logs -f $(OCR_FRONTEND_CONTAINER)

clean: ## Nettoyage du dépôt
	rm -rf __pycache__ .pytest_cache .ruff_cache .mypy_cache
	rm -rf frontend/node_modules frontend/.nuxt frontend/.output
	$(MAKE) down

clean-front: ## Nettoyage du frontend
	rm -rf apps/client/node_modules apps/client/.nuxt apps/client/.output
	$(MAKE) down-frontend

build: build-ocr-backend build-ocr-service ## Lance la construction de toutes les images Docker

build-container-dependencies: ## Build docker dependecies
	docker compose -f docker-compose-test.yaml build minio redis db migration


build-ocr-backend: ## Lance la construction de l'image Docker backend
	docker compose build ocr_backend

build-ocr-service: ## Lance la construction de l'image Docker service
	docker compose build ocr_service

build-ocr-frontend: ## Lance la construction de l'image Docker frontend
	docker compose -f docker-compose.vue.yaml build ocr_frontend

upgrade-db: ## Applique les migrations de base de données
	docker compose run --rm migration alembic upgrade head

stamp-db: ## Change le pointeur alembic à une révision particulière
	@read -p "id de la révision : " revision; \
	docker compose run --rm migration alembic stamp $$revision

list-revision: ## Liste les révisions de la base de données
	docker compose run --rm migration alembic history
upgrade-revision: ## Crée une nouvelle révision de base de données
	@read -p "Message de révision : " msg; \
	docker compose run --rm migration alembic revision --autogenerate -m "$$msg"

cluster: ## Crée un cluster Kind local
	kind create cluster --name ocr --config ./kind/config.yaml

load-image: ## Upload les images dans le cluster
	docker image tag ocr-api:latest ocr-api:v1
	docker image tag ocr-service-paddle:latest ocr-service-paddle:v1
	kind load docker-image ocr-service-paddle:v1 ocr-api:v1 --name ocr

stress-test: install-uv ## Lance un test de charge
	uv run locust -f stress-script/1-stress-test.py --host $(STRESS_HOST)

stress-stats: install-uv ## Affiche les statistiques du test de charge
	STRESS_HOST=$(STRESS_HOST) uv run stress-script/2-process-stats.py

test-services-checkbox: build-container-dependencies ## Test checkboxes algo
	docker compose -f docker-compose-test.yaml up checkbox_service
	make down-test

test-services-paddleocr2.10.0: build-container-dependencies ## Test PaddleOCR 2.10.0
	docker compose -f docker-compose-test.yaml up paddleocr2_service
	make down-test

test-services-paddleocr3.1.0: build-container-dependencies ## Test PaddleOCR 3.1.0
	docker compose -f docker-compose-test.yaml up paddleocr3_service
	make down-test
test-services-llm: build-container-dependencies  ## Test LLM integration
	docker compose -f docker-compose-test.yaml up llm_ocr_service
	make down-test

test-services-forms: build-container-dependencies  ## Test Forms integration
	docker compose -f docker-compose-test.yaml up forms_service
	make down-test

test-services-paddleocr3.1.0-gpu: build-container-dependencies  ## Test PaddleOCR 3.1.0 with gpu
ifeq ($(HAS_GPU),yes)
	@echo "✅ GPU detected. Running GPU tests..."
	sudo docker compose -f docker-compose-test.yaml build paddleocr3_service_gpu
	sudo docker compose -f docker-compose-test.yaml up paddleocr3_service_gpu
	make down-test
else
	@echo "⚠️ No GPU detected. Skipping GPU tests. But build the image"
	docker compose -f docker-compose-test.yaml build paddleocr3_service_gpu
endif

test-backend-api: build-container-dependencies  ## Test ocr backend
	docker compose -f docker-compose-test.yaml up ocr_backend
	make down-test

generate-openapi: up-frontend  ## Génère la documentation OpenAPI
	docker compose -f docker-compose.vue.yaml exec ocr_frontend pnpm run generate-openapi
