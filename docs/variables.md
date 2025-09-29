## Environment Variables

Ce projet utilise plusieurs variables d'environnement pour configurer les modèles OCR, Celery, les connecteurs de stockage (MinIO / S3), Redis, ainsi que le monitoring des ressources.

Les variables sont chargées automatiquement grâce à [`pydantic-settings`](https://docs.pydantic.dev/latest/concepts/pydantic_settings/).

---

### Variables liées à PaddleOCR

| Variable | Description | Default | Utilisation |
|:---|:---|:---|:---|
| `PADDLE_OCR_BASE_DIR` | Chemin de base où sont stockés les modèles OCR. | `models/` | `ocr_service` |
| `DETECTION_FOLDER` | Sous-dossier du modèle de détection. | `detection` | `ocr_service` |
| `RECOGNITION_FOLDER` | Sous-dossier du modèle de reconnaissance. | `recognition` | `ocr_service` |
| `CLASSIFICATION_FOLDER` | Sous-dossier du modèle de classification. | `classification` | `ocr_service` |
| `DETECTION_BATCH_SIZE` | Batch size pour la détection. | `2` | `ocr_service` |
| `RECOGNITION_BATCH_SIZE` | Batch size pour la reconnaissance. | `4` | `ocr_service` |

---

### Variable liée au choix du modèle LLM

| Variable           | Description                                      | Default      | Utilisation    |
|:-------------------|:------------------------------------------------|:-------------|:---------------|
| `OPENAI_API_KEY`   | Clé API OpenAI pour accéder aux modèles LLM.     | (aucune)     | `ocr_service`  |
| `OPENAI_BASE_URL`  | URL de l’API OpenAI (ex : https://api.openai.com/v1). | (aucune)     | `ocr_service`  |
| `VISION_MODEL_NAME`| Nom du modèle de vision à utiliser.              | `gpt-4-vision` | `ocr_service`  |

---

### Variable liée au choix du modèle OCR

| Variable | Description | Default | Utilisation |
|:---|:---|:---|:---|
| `MODEL_NAME` | Choix du modèle OCR (`paddle` ou `surya`). | `paddle` | `ocr_service`, `OCRModelSettings` |

---

### Variables pour la configuration Celery

| Variable | Description | Default | Utilisation |
|:---|:---|:---|:---|
| `CELERY_APP_NAME` | Nom de l'application Celery. | `default` | `CelerySettings` |

---

### Variables pour la configuration du connecteur de stockage

| Variable | Description | Default | Utilisation |
|:---|:---|:---|:---|
| `S3_AVAILABLE` | Active ou non le connecteur S3 (`True` ou `False`). | `False` | `ConnectorSettings` |
| `MINIO_AVAILABLE` | Active ou non le connecteur MinIO (`True` ou `False`). | `True` | `ConnectorSettings` |

> ⚡ **Important :** `S3_AVAILABLE` et `MINIO_AVAILABLE` **ne doivent pas être tous les deux à `True`**.

---

### Variables spécifiques à MinIO (si `MINIO_AVAILABLE=True`)

| Variable | Description | Default | Utilisation |
|:---|:---|:---|:---|
| `MINIO_BUCKET_NAME` | Nom du bucket MinIO. | `test` | `MinioSettings` |
| `MINIO_END_POINT` | Adresse du serveur MinIO. | `localhost:9000` | `MinioSettings` |
| `MINIO_ACCESS_KEY` | Identifiant d'accès MinIO. | `minioadmin` | `MinioSettings` |
| `MINIO_SECRET_KEY` | Mot de passe MinIO. | `minioadmin` | `MinioSettings` |

---

### Variables spécifiques à S3 (si `S3_AVAILABLE=True`)

| Variable | Description | Default | Utilisation |
|:---|:---|:---|:---|
| `S3_BUCKET_NAME` | Nom du bucket S3. | `test` | `S3Settings` |
| `S3_END_POINT` | Adresse du endpoint S3. | `localhost:9000` | `S3Settings` |
| `S3_ACCESS_KEY` | Identifiant d'accès S3. | `S3admin` | `S3Settings` |
| `S3_SECRET_KEY` | Mot de passe S3. | `S3admin` | `S3Settings` |
| `S3_REGION` | Région du bucket S3. | `fr-par` | `S3Settings` |

---

### Variables pour la configuration Redis

| Variable | Description | Default | Utilisation |
|:---|:---|:---|:---|
| `REDIS_HOST` | Adresse du serveur Redis. | `localhost` | `RedisSettings` |
| `REDIS_PORT` | Port Redis. | `6379` | `RedisSettings` |
| `REDIS_QUEUE_NAME` | Nom de la file Redis pour Celery. | `redis-queue` | `RedisSettings` |

---

### Variables pour la configuration du tracing Langfuse

| Variable | Description | Default | Utilisation |
|:---|:---|:---|:---|
| `TRACING_SERVICE` | Service de tracing à utiliser (`langfuse` ou `logging`). | `logging` | `TracingService` |
| `LANGFUSE_PUBLIC_KEY` | Clé publique Langfuse pour l'authentification. | (aucune) | `LangFuseTracingService` |
| `LANGFUSE_SECRET_KEY` | Clé secrète Langfuse pour l'authentification. | (aucune) | `LangFuseTracingService` |
| `LANGFUSE_HOST` | URL du serveur Langfuse (ex: https://cloud.langfuse.com). | (aucune) | `LangFuseTracingService` |
| `LANGFUSE_DEBUG` | Active le mode debug Langfuse (`true` ou `false`). | `false` | `LangFuseTracingService` |
| `LANGFUSE_TRACING_ENVIRONMENT` | Environnement de tracing (ex: `dev`, `preprod`, `prod`). | `dev` | `LangFuseTracingService` |

---

### Variables diverses

| Variable | Description | Default | Utilisation |
|:---|:---|:---|:---|
| `MONITOR_RESSOURCE_EVERY` | Fréquence (en secondes) pour monitorer la consommation de ressources d'une tâche. | `5` (exemple) | `resource_monitor` dans les tâches |
| `DATABASE_URL` | URL de connexion à la base de données PostgreSQL. | - | Utilisée dans l'ORM (`task_table`, etc.) |

---

## Exemple de fichier `.env`

```dotenv
# PaddleOCR
PADDLE_OCR_BASE_DIR=models/
DETECTION_FOLDER=detection
RECOGNITION_FOLDER=recognition
CLASSIFICATION_FOLDER=classification
DETECTION_BATCH_SIZE=2
RECOGNITION_BATCH_SIZE=4

# OCR Model
MODEL_NAME=paddle

# Celery
CELERY_APP_NAME=my-celery-app

# Connecteurs de stockage
S3_AVAILABLE=False
MINIO_AVAILABLE=True

# Minio
MINIO_BUCKET_NAME=test
MINIO_END_POINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# S3 (si besoin)
S3_BUCKET_NAME=test
S3_END_POINT=localhost:9000
S3_ACCESS_KEY=S3admin
S3_SECRET_KEY=S3admin
S3_REGION=fr-par

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_QUEUE_NAME=redis-queue

# Tracing Langfuse
TRACING_SERVICE=langfuse
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxxxxxxxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxxxxxxxxxxxxxx
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_DEBUG=true
LANGFUSE_TRACING_ENVIRONMENT=preprod

# Monitoring
MONITOR_RESSOURCE_EVERY=5

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```
