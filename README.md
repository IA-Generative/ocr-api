
# OCR API

---


##  Installation

### Avec `uv`
```bash
uv sync
```

### Avec Docker
```bash
make build-ocr-backend
make build-ocr-service
make up-env # that let you run Minio and Redis
```

---

## Lancement de l’API

### En local avec Python
```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 5000 --workers 2
```

### Avec Docker Compose
```bash
docker compose -f docker-compose.yaml up -d
```

Accède ensuite à l'API via : [http://localhost:5000](http://localhost:5000)

---

## Tester l’API
### Tester avec `curl`

```bash
curl -X 'POST' \
  'http://localhost:5000/?grayscale=false&return_image=false' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@2109.10282v5.pdf;type=application/pdf'
```

## Test de charge (stress test)

Utilisation de `locust` :

```bash
uv add locust --group stress-test
uv run locust -f stress-test.py --host http://localhost:5000 \
  --headless -u 2 -r 10 --run-time 2m --csv results
```

## Diagramme execution 
<img src= "docs/Diagrame.drawio.png" title="qsqs"></img>

```mermaid
flowchart TD
    A[Client envoie un document image/pdf] --> B[API Python reçoit le fichier]
    B --> C[Le fichier est sauvegardé dans MinIO]
    C --> D[Création de la task en BDD -task_id, status = CREATED]
    D --> E[Envoi de la task dans la queue Redis]
    E --> F[Queue FIFO Redis]
    F --> G[Consommateur OCR récupère une tâche - pas de doublon]
    G --> H[Récupération du fichier depuis MinIO]
    H --> I[OCR en cours - Mise à jour du status en BDD à chaque étape]
    I --> J[Status de la task disponible via l'API]
    J --> K[Retour de l’état de la task avec/sans résultats]

    classDef store fill:#f9f,stroke:#333,stroke-width:1px;
    class C,H store;

    classDef queue fill:#bbf,stroke:#333,stroke-width:1px;
    class E,F queue;

    classDef api fill:#bfb,stroke:#333,stroke-width:1px;
    class B,J,K api;

    classDef db fill:#ffb,stroke:#333,stroke-width:1px;
    class D,I db;

    classDef process fill:#eef,stroke:#333,stroke-width:1px;
    class G process;
```



### Diagram Sequence
```mermaid
sequenceDiagram
    participant Client
    participant API
    participant MinIO
    participant BDD
    participant Redis
    participant Consommateur_OCR

    Client->>API: Envoi document (image/pdf)
    API->>MinIO: Sauvegarde du fichier
    API->>BDD: Création task (task_id, status=CREATED)
    API->>Redis: Push task dans la queue

    Redis->>Consommateur_OCR: Délivre task (FIFO, sans doublon)
    Consommateur_OCR->>MinIO: Récupération du fichier
    Consommateur_OCR->>BDD: Maj status étape par étape (processing...)

    Client->>API: Demande status task
    API->>BDD: Lecture status task
    API-->>Client: Retour état + résultats si dispo

```