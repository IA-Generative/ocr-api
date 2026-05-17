# Guide d'installation

## Prérequis

| Outil            | Description                                                                 |
|------------------|-----------------------------------------------------------------------------|
| Docker           | [Installer Docker](https://docs.docker.com/get-docker/)                    |
| Docker Compose   | [Installer Docker Compose](https://docs.docker.com/compose/) (v2+ recommandé) |

## Configuration des variables d'environnement

| Variable                  | Description                                                                 | Utilisation                                                                 |
|---------------------------|-----------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| `REDIS_HOST`              | Adresse de l'hôte Redis                                                   | Utilisé par Celery pour la gestion des tâches asynchrones                  |
| `REDIS_PORT`              | Port utilisé par Redis                                                    | Utilisé par Celery pour la gestion des tâches asynchrones                  |
| `REDIS_QUEUE_NAME`        | Nom de la file d'attente Redis                                            | Définit la file d'attente pour les tâches Celery                           |
| `DATABASE_URL`            | Chaîne de connexion à la base de données PostgreSQL                      | Connexion à la base de données principale                                 |
| `MONITOR_RESSOURCE_EVERY` | Intervalle de surveillance des ressources (en secondes)                  | Définit la fréquence de surveillance des ressources système               |
| `S3_BUCKET_NAME`          | Nom du bucket S3 (MinIO)                                                 | Stockage des fichiers OCR                                                 |
| `AWS_ACCESS_KEY_ID`       | Clé d'accès AWS pour MinIO                                               | Authentification pour accéder au stockage MinIO                           |
| `AWS_SECRET_ACCESS_KEY`   | Clé secrète AWS pour MinIO                                               | Authentification pour accéder au stockage MinIO                           |
| `AWS_ENDPOINT_URL`        | URL de l'endpoint MinIO                                                 | URL pour accéder au service MinIO                                         |
| `AWS_DEFAULT_REGION`      | Région par défaut pour S3                                                | Région par défaut pour les opérations S3                                  |
| `TERM`                    | Configuration du terminal                                                | Configuration de l'environnement terminal                                 |
| `PROCESS_NAME`            | Nom du processus OCR                                                    | Identification du processus OCR                                           |
| `WORKER_NAME`             | Nom du worker pour les tâches OCR                                       | Identification du worker Celery                                           |
| `DEVICE`                  | Type de périphérique utilisé (ex: `cpu`)                                | Définit le périphérique pour l'exécution des modèles OCR                  |
| `OPENAI_API_KEY`          | Clé API pour accéder aux services OpenAI                                   | Utilisé pour les modèles d'IA et les embeddings                           |
| `OPENAI_BASE_URL`         | URL de base pour les services OpenAI                                      | Définit l'endpoint pour les requêtes OpenAI                              |
| `EMBEDDINGS_MODEL`        | Modèle utilisé pour les embeddings                                       | Utilisé pour retrouver les sources probables à une réponse et pour l'extraction d'entités |
| `OPENAI_MODEL`            | Modèle OpenAI utilisé                                                   | Utilisé dans le chatbot, pour la classification et l'extraction d'entités |
| `OPENAI_VISION_MODEL`     | Modèle OpenAI pour la vision                                            | Utilisé dans les layouts pour décrire une image ou formater un tableau en sortie |
| `DATABASE_ASYNC_URL`      | Chaîne de connexion asynchrone à la base de données PostgreSQL          | Utilisé pour les opérations asynchrones avec la base de données         |
| `S3_PUBLIC_URL`           | URL publique pour accéder au stockage S3                                | Permet d'accéder aux fichiers stockés dans MinIO                        |
| `VERIFY_SSL`              | Indique si SSL doit être vérifié                                        | Utilisé pour les connexions sécurisées                                  |
| `MINIO_ROOT_USER`         | Utilisateur root pour MinIO                                             | Authentification pour l'administration de MinIO                         |
| `MINIO_ROOT_PASSWORD`     | Mot de passe root pour MinIO                                            | Authentification pour l'administration de MinIO                         |
| `PADDLE_OCR_BASE_DIR`     | Répertoire de base pour les modèles PaddleOCR                          | Définit l'emplacement des modèles OCR                                  |
| `PADDLE_PDX_CACHE_HOME`   | Répertoire de cache pour PaddlePaddle                                  | Définit l'emplacement du cache pour PaddlePaddle                       |
| `PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK` | Désactive la vérification de la source des modèles PaddlePaddle | Optimisation pour éviter les vérifications inutiles                     |
| `ENVIRONMENT`             | Environnement d'exécution (ex: `development`)                          | Définit l'environnement pour le backend                                 |
| `SERVICE_NAME`            | Nom du service OCR                                                     | Identification du service dans les logs et les métriques               |
| `CELERY_APP_NAME`         | Nom de l'application Celery                                            | Identification de l'application pour les tâches asynchrones             |
| `VERIFY_TOKEN_MODEL`      | Modèle de vérification des jetons                                      | Trois valeurs possibles : `full-access` (accès complet sans authentification), `dev`, et `keycloak` (voir fichier factory.py) |

Ajoutez ces variables dans un fichier `.env` à la racine du projet.

---

## Lancer l’application (Backend)

Depuis la racine du projet, lancez la commande suivante :

```bash
docker compose up --build -d
```

Cette commande construit les images si nécessaire et démarre tous les conteneurs en arrière-plan.