## Environment Variables

Ce projet utilise plusieurs variables d'environnement pour configurer les modèles OCR, Celery, les connecteurs de stockage (MinIO / S3), Redis, la base de données, ainsi que le monitoring des ressources.

Les variables sont chargées automatiquement grâce à [`pydantic-settings`](https://docs.pydantic.dev/latest/concepts/pydantic_settings/), sauf mention contraire (certaines sont lues directement via `os.environ`).

Légende : ✅ = obligatoire (le service plante/refuse de démarrer si absente) — ❌ = optionnelle (valeur par défaut fournie par le code).

---

### Variables liées à PaddleOCR

| Variable | Obligatoire | Description | Default | Utilisation |
|:---|:---:|:---|:---|:---|
| `PADDLE_OCR_BASE_DIR` | ❌ | Chemin de base où sont stockés les modèles OCR. | `models/` | `PaddleSetting` |
| `PADDLE_PDX_CACHE_HOME` | ❌ | Cache PaddleX (téléchargement/chargement des modèles). | `models/paddle_pdx_cache/` | `PaddleSetting` |
| `DETECTION_FOLDER` | ❌ | Sous-dossier du modèle de détection. | `detection` | `PaddleSetting` |
| `RECOGNITION_FOLDER` | ❌ | Sous-dossier du modèle de reconnaissance. | `recognition` | `PaddleSetting` |
| `CLASSIFICATION_FOLDER` | ❌ | Sous-dossier du modèle de classification. | `classification` | `PaddleSetting` |
| `DETECTION_BATCH_SIZE` | ❌ | Batch size pour la détection. | `2` | `PaddleSetting` |
| `RECOGNITION_BATCH_SIZE` | ❌ | Batch size pour la reconnaissance. | `8` | `PaddleSetting` |
| `CPU_THREADS` | ❌ | Nombre de threads CPU pour l'inférence PaddleOCR. | `2` | `PaddleSetting` |
| `ENABLE_MKLDNN` | ❌ | Active l'accélération MKL-DNN. | `False` | `PaddleSetting` |
| `OCR_VERSION` | ❌ | Version du modèle PaddleOCR. | `PP-OCRv3` | `PaddleSetting` |
| `DEVICE` | ❌ | Device d'inférence (`cpu`/`gpu`). | `cpu` | `PaddleSetting` |
| `OCR_LANG` | ❌ | Langue forcée pour l'OCR. | `None` | `PaddleSetting` |

---

### Variable liée au choix du modèle LLM

| Variable | Obligatoire | Description | Default | Utilisation |
|:---|:---:|:---|:---|:---|
| `OPENAI_API_KEY` | ✅ | Clé API OpenAI pour accéder aux modèles LLM. | - | `OpenAISetting` (`business/llm/config.py`) |
| `OPENAI_BASE_URL` | ✅ | URL de l'API OpenAI (ex : https://api.openai.com/v1). | - | `OpenAISetting` |
| `INSTRUCT_MODEL_NAME` | ✅ | Nom du modèle d'instruction utilisé. | - | `OpenAISetting` |
| `VISION_MODEL` | ❌ | Nom du modèle de vision à utiliser. | `None` | `OpenAISetting` |

---

### Variable liée au choix du modèle OCR

| Variable | Obligatoire | Description | Default | Utilisation |
|:---|:---:|:---|:---|:---|
| `MODEL_NAME` | ❌ | Choix du modèle OCR (`paddle` ou `surya`). | `paddle` | `OCRModelSettings` |
| `USE_VISION_LLM_EXTRACT_KIE` | ❌ | Active l'extraction KIE via un LLM de vision. | `False` | `OCRModelSettings` |

---

### Variables pour la configuration Celery

| Variable | Obligatoire | Description | Default | Utilisation |
|:---|:---:|:---|:---|:---|
| `CELERY_APP_NAME` | ❌ | Nom de l'application Celery. | `default` | `CelerySettings` |
| `WORKER_NAME` | ✅ | Nom du worker (identifie le pod/process dans les logs). | - | lu via `os.environ` dans `services/main.py` |
| `PROCESS_NAME` | ✅ | Nom du pipeline OCR à charger dans ce worker. | - | lu via `os.environ` dans `services/main.py` |

---

### Variables pour la configuration du connecteur de stockage

| Variable | Obligatoire | Description | Default | Utilisation |
|:---|:---:|:---|:---|:---|
| `S3_AVAILABLE` | ❌ | Active ou non le connecteur S3 (`True` ou `False`). | `False` | `ConnectorSettings` |
| `MINIO_AVAILABLE` | ❌ | Active ou non le connecteur MinIO (`True` ou `False`). | `True` | `ConnectorSettings` |

> ⚡ **Important :** `S3_AVAILABLE` et `MINIO_AVAILABLE` **ne doivent pas être tous les deux à `True`**.

---

### Variables spécifiques à MinIO (si `MINIO_AVAILABLE=True`)

| Variable | Obligatoire | Description | Default | Utilisation |
|:---|:---:|:---|:---|:---|
| `MINIO_BUCKET_NAME` | ❌ | Nom du bucket MinIO. | `test` | `MinioSettings` |
| `MINIO_END_POINT` | ❌ | Adresse du serveur MinIO. | `localhost:9000` | `MinioSettings` |
| `MINIO_ACCESS_KEY` | ❌ | Identifiant d'accès MinIO. | `minioadmin` | `MinioSettings` |
| `MINIO_SECRET_KEY` | ❌ | Mot de passe MinIO. | `minioadmin` | `MinioSettings` |

---

### Variables spécifiques à S3 (si `S3_AVAILABLE=True`)

| Variable | Obligatoire | Description | Default | Utilisation |
|:---|:---:|:---|:---|:---|
| `S3_BUCKET_NAME` | ❌ | Nom du bucket S3. | `test` | `S3Settings` |
| `S3_END_POINT` | ❌ | Adresse du endpoint S3. | `localhost:9000` | `S3Settings` |
| `S3_ACCESS_KEY` | ❌ | Identifiant d'accès S3. | `S3admin` | `S3Settings` |
| `S3_SECRET_KEY` | ❌ | Mot de passe S3. | `S3admin` | `S3Settings` |
| `S3_REGION` | ❌ | Région du bucket S3. | `fr-par` | `S3Settings` |
| `VERIFY_SSL` | ❌ | Vérifie le certificat SSL du endpoint S3. | `False` | `S3Settings` |

---

### Variables pour la configuration Redis

Redis est utilisé comme broker Celery (`RedisSettings`, `src/config/redis.py` + `src/connector/broker_connector.py`) et pour le health-check applicatif.

| Variable | Obligatoire | Description | Default | Utilisation |
|:---|:---:|:---|:---|:---|
| `REDIS_HOST` | ❌ | Adresse du serveur Redis (ignorée si le mode Sentinel est activé). | `localhost` | `RedisSettings` |
| `REDIS_PORT` | ❌ | Port Redis (ignoré si le mode Sentinel est activé). | `6379` | `RedisSettings` |
| `REDIS_DB` | ❌ | Index de la base logique Redis. | `0` | `RedisSettings` |
| `REDIS_PASSWORD` | ❌ | Mot de passe Redis (recommandé en prod). | `None` | `RedisSettings` |
| `REDIS_USE_TLS` | ❌ | Active TLS (`rediss://`) pour la connexion Redis. | `False` | `RedisSettings` |
| `REDIS_SENTINEL_ENABLED` | ❌ | Active la résolution du master via Redis Sentinel. | `False` | `RedisSettings` |
| `REDIS_SENTINEL_HOSTS` | ❌ (✅ si Sentinel activé) | Liste `host:port` séparée par des virgules des sentinels. | `None` | `RedisSettings` |
| `REDIS_SENTINEL_MASTER_NAME` | ❌ | Nom du master surveillé par les sentinels. | `mymaster` | `RedisSettings` |
| `REDIS_SENTINEL_PASSWORD` | ❌ | Mot de passe pour l'authentification auprès des sentinels (retombe sur `REDIS_PASSWORD` si absent pour le broker). | `None` | `RedisSettings` |

> ℹ️ `REDIS_QUEUE_NAME` a été retiré de cette documentation : la variable n'est référencée nulle part dans le code (documentation obsolète).
>
> Si Redis est géré par un chart (ex: Bitnami) avec réplication + Sentinel, préférez laisser le chart exposer un unique service Sentinel et ne renseignez que `REDIS_SENTINEL_ENABLED`/`REDIS_SENTINEL_HOSTS`/`REDIS_SENTINEL_MASTER_NAME` — le master courant sera résolu dynamiquement à chaque connexion.

---

### Variables pour la configuration du tracing Langfuse

| Variable | Obligatoire | Description | Default | Utilisation |
|:---|:---:|:---|:---|:---|
| `TRACING_SERVICE` | ❌ | Service de tracing à utiliser (`langfuse` ou `logging`). | `logging` | lu via `os.environ` |
| `LANGFUSE_PUBLIC_KEY` | ❌ | Clé publique Langfuse pour l'authentification. | - | `LangFuseTracingService` |
| `LANGFUSE_SECRET_KEY` | ❌ | Clé secrète Langfuse pour l'authentification. | - | `LangFuseTracingService` |
| `LANGFUSE_HOST` | ❌ | URL du serveur Langfuse (ex: https://cloud.langfuse.com). | - | `LangFuseTracingService` |
| `LANGFUSE_DEBUG` | ❌ | Active le mode debug Langfuse (`true` ou `false`). | `false` | `LangFuseTracingService` |
| `LANGFUSE_TRACING_ENVIRONMENT` | ❌ | Environnement de tracing (ex: `dev`, `preprod`, `prod`). | `dev` | `LangFuseTracingService` |

---

### Variables diverses

| Variable | Obligatoire | Description | Default | Utilisation |
|:---|:---:|:---|:---|:---|
| `MONITOR_RESSOURCE_EVERY` | ❌ | Fréquence (en secondes) pour monitorer la consommation de ressources d'une tâche. | `5` (exemple) | `resource_monitor` dans les tâches |
| `DATABASE_URL` | ✅ | URL de connexion à la base de données PostgreSQL. Obligatoire pour le job de migration (`migration/env.py`, plante sans fallback) ; l'application applicative retombe silencieusement sur SQLite local si absente (log `WARNING`) — **ne pas compter sur ce fallback en prod, uniquement pour du dev/test local**. | - (fallback SQLite local en dehors de la migration) | `migration/env.py`, `src/connector/db_connector.py` |
| `ENVIRONMENT` | ❌ | Environnement d'exécution (`development`, `production`, ...). | - | `services/main.py`, `src/logger.py`, `ocr_backend/main.py` |
| `SERVICE_NAME` | ❌ | Nom du service pour les logs structurés. | - | `src/logger.py` |
| `API_KEYS` | ❌ | Clés API acceptées par l'API backend. | - | `ocr_backend/core/security/factory.py` |
| `KEYCLOAK_URL` / `KEYCLOAK_REALM` / `KEYCLOAK_CLIENT_ID` / `KEYCLOAK_CLIENT_SECRET` / `VERIFY_TOKEN_MODEL` | ❌ | Configuration Keycloak pour l'auth OIDC. | - | `ocr_backend/core/security/factory.py` |
| `MODEL_FEATURE_NAME` | ❌ | Nom du modèle de features utilisé par les collections. | - | `ocr_backend/routers/collections.py` |

---

## Volumes

| Volume | Type | Point de montage | Usage |
|:---|:---|:---|:---|
| `postgres_data` | volume nommé (PVC en cluster) | `/var/lib/postgresql/data` | Données PostgreSQL — **doit être persistant**. |
| `minio_data` | volume nommé (PVC en cluster) | `/data` | Stockage objet MinIO (dev-only, remplacé par du vrai S3 en prod). |

> ⚠️ **Pas de volume dédié pour le cache de modèles PaddleOCR** (`PADDLE_OCR_BASE_DIR` / `PADDLE_PDX_CACHE_HOME`) : les modèles sont téléchargés et intégrés à l'image Docker au build (`business/paddleocr2/Dockerfile`), pas montés en volume à l'exécution. Chaque rebuild d'image retélécharge les modèles, et il n'y a pas de cache partagé entre replicas/pods. À considérer côté infra si la taille d'image ou le temps de démarrage posent problème.
>
> Les autres montages (`docker-compose.yaml`) sont des bind-mounts de code source pour le hot-reload en dev — non pertinents pour un déploiement en cluster.

---

## Exemple de fichier `.env`

```dotenv
# PaddleOCR
PADDLE_OCR_BASE_DIR=models/
DETECTION_FOLDER=detection
RECOGNITION_FOLDER=recognition
CLASSIFICATION_FOLDER=classification
DETECTION_BATCH_SIZE=2
RECOGNITION_BATCH_SIZE=8

# LLM (obligatoire)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxx
OPENAI_BASE_URL=https://api.openai.com/v1
INSTRUCT_MODEL_NAME=gpt-4o-mini

# OCR Model
MODEL_NAME=paddle

# Celery (WORKER_NAME/PROCESS_NAME sont injectés par worker dans docker-compose.yaml)
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
REDIS_DB=0
REDIS_PASSWORD=
REDIS_USE_TLS=False
# Sentinel (optionnel, prioritaire sur REDIS_HOST/REDIS_PORT si activé)
REDIS_SENTINEL_ENABLED=False
REDIS_SENTINEL_HOSTS=sentinel-0:26379,sentinel-1:26379,sentinel-2:26379
REDIS_SENTINEL_MASTER_NAME=mymaster
REDIS_SENTINEL_PASSWORD=

# Tracing Langfuse
TRACING_SERVICE=langfuse
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxxxxxxxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxxxxxxxxxxxxxx
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_DEBUG=true
LANGFUSE_TRACING_ENVIRONMENT=preprod

# Monitoring
MONITOR_RESSOURCE_EVERY=5

# Database (obligatoire)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```
