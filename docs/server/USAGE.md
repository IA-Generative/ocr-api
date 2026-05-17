# Usage de l'application OCR API

## Accès aux services

| Service                  | URL                              | Identifiants          |
|--------------------------|----------------------------------|-----------------------|
| API OCR (FastAPI)        | [http://localhost:5000](http://localhost:5000) | -                     |
| Interface MinIO          | [http://localhost:9001](http://localhost:9001) | Identifiant : `minioadmin`<br>Mot de passe : `minioadmin` |
| Monitoring Celery (Flower) | [http://localhost:5555](http://localhost:5555) | -                     |
| Interface Frontend        | [http://localhost:8081](http://localhost:8081) | -                     |


## Arrêter l’application

Pour stopper et supprimer les conteneurs, exécutez :

```bash
docker compose down
```

Pour supprimer également les volumes persistants (base de données, MinIO), ajoutez l’option `-v` :

```bash
docker compose down -v
```

## Tester l’API

Vous pouvez tester l’API OCR avec un script simple, par exemple :

```bash
curl -X POST "http://localhost:5000/jobs/ton_user_id" \
  -F "file=@/chemin/vers/ton/fichier.jpg"
```

Obtenir l'état de la tâche :

```bash
curl -X GET "http://localhost:5000/tasks/ton_task_id"
```