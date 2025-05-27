IMAGE_NAME_OCR_BACKEND=ocr-api
IMAGE_NAME_OCR_SERVICE=ocr-service
PYTHONPATH=$(PWD)
OCR_BACKEND_CONTAINER=ocr-api
OCR_SERVICE_CONTAINER=ocr-service
STRESS_HOST=http://localhost:5000


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

lint: install ## Lint le code du dépôt
	uv run ruff check .

bump:
	@echo "Usage: make bump-patch OR make bump-minor"

bump-patch:
	uv run cz bump --increment patch

bump-minor:
	uv run cz bump --increment minor

up: ## Lance l'environnement de développement en conteneurs
	docker compose up -d

down: ## Eteint l'environnement de développement en conteneurs
	docker compose down || true

logs-api: ## Affiche les logs du conteneur de l'API
	docker logs -f $(OCR_BACKEND_CONTAINER)

logs-service: ## Affiche les logs du conteneur de service
	docker logs -f $(OCR_SERVICE_CONTAINER)

clean: ## Nettoyage du dépôt
	rm -rf __pycache__ .pytest_cache .ruff_cache .mypy_cache
	$(MAKE) down

tests: up ## Lance les tests unitaires
	docker exec $(OCR_BACKEND_CONTAINER) pytest --cov=./ocr_backend --cov=./src --cov-report=term-missing tests/ocr_backend tests/src/
	docker exec $(OCR_SERVICE_CONTAINER) pytest --cov=./ocr_service tests/ocr_service

build: build-ocr-backend build-ocr-service ## Lance la construction de toutes les images Docker


build-ocr-backend: ## Lance la construction de l'image Docker backend
	docker compose build ocr_backend

build-ocr-service: ## Lance la construction de l'image Docker service
	docker compose build ocr_service

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
