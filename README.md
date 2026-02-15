
# OCR API

Cette API fournit un service d’extraction de texte à partir de fichiers PDF ou d’images. Elle repose sur un pipeline de traitement asynchrone utilisant Redis (queue), S3 (stockage), et PaddleOCR pour effectuer la reconnaissance de texte.

## Démo

![DEMO](docs/images/demo-ocr.gif)

## SDK Python

Un SDK Python est disponible pour faciliter l'intégration de l'API OCR dans vos projets. Le SDK supporte les clients synchrones et asynchrones avec des modèles Pydantic pour une validation stricte des données.

📦 **[Voir le SDK](sdk/README.md)** - Client Python avec support async/sync

### Installation rapide du SDK

```bash
cd sdk
uv pip install -e .
# ou
pip install -e .
```

### Utilisation du SDK

```python
from ocr_sdk import SyncOCRClient

with SyncOCRClient("http://localhost:5000") as client:
    task = client.create_job("document.pdf")
    result = client.wait_for_task(task.id)
    text = client.get_task_text(task.id)
    print(text)
```

Pour plus de détails, consultez la [documentation du SDK](sdk/README.md).

## [Fonctionnement](docs/server/asyncronus.md)

Dans cette section vous trouverez le fonctionnement de cette application [docs/server/asyncronus.md](docs/server/asyncronus.md)

## Prérequis

- [Docker](https://docs.docker.com/get-docker/) installé
- [Docker Compose](https://docs.docker.com/compose/) (version 2+ recommandée)
- Un fichier `.env` configuré à la racine du projet (voir exemple ci-dessous)

---

## Configuration du fichier `.env`

Crée un fichier `.env` à la racine avec les variables suivantes (à adapter si besoin) :

```env
# Redis configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_QUEUE_NAME=redis-queue

# Database connection string (PostgreSQL)
DATABASE_URL=postgresql://postgres:secret@db:5432/example_db

# Monitoring interval (seconds)
MONITOR_RESSOURCE_EVERY=5

# S3 (MinIO) configuration
S3_BUCKET_NAME=test
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
AWS_ENDPOINT_URL=http://minio:9000
AWS_DEFAULT_REGION=us-east-1

# Terminal settings
TERM=xterm-256color
no_proxy=minio

# OCR worker settings
PROCESS_NAME="mixed-classic-and-vlm"
WORKER_NAME=worker.tasks.ocr
DEVICE=cpu

````

---

## Lancer l’application (Backend)

Depuis la racine du projet, lance la commande :

```bash
docker compose up --build -d
```

Cette commande construit les images si nécessaire et démarre tous les containers en arrière-plan.

---

## Accès aux services

- API OCR (FastAPI) : [http://localhost:5000](http://localhost:5000)
- Interface MinIO : [http://localhost:9001](http://localhost:9001)
  — Identifiant : `minioadmin`
  — Mot de passe : `minioadmin`
- Monitoring Celery (Flower) : [http://localhost:5555](http://localhost:5555)

---

## Arrêter l’application

Pour stopper et supprimer les containers, exécute :

```bash
docker compose down
```

Pour supprimer aussi les volumes persistants (base de données, MinIO), ajoute l’option `-v` :

```bash
docker compose down -v
```

---

## Tester l’API

Tu peux tester l’API OCR avec un script simple, par exemple :

```bash
curl -X POST "http://localhost:5000/jobs/ton_user_id" \
  -F "file=@/chemin/vers/ton/fichier.jpg"
```

Obtenir l'état de la taches :

```bash
curl -X GET "http://localhost:5000/tasks/ton_task_id"
```
Vous pouvez aussi passé par l'ui dédié [Frontend](#frontend)

---

## Support et dépannage

- Assure-toi que Docker et Docker Compose sont correctement installés
- Vérifie que le fichier `.env` est présent et bien configuré

## Frontend

### Installation

Utilisation d'un Makefile pour exécuter les commandes ***(installation de `make` requis)***.

```sh
# Démarrer l'environnement de développement
make up-frontend

# Démarrer & mettre à jour les types
make generate-openapi
```
