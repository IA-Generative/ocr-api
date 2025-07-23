
# OCR API

Une API permettant d'extraire du texte à partir de documents (PDF/images) à l’aide d’un pipeline asynchrone basé sur Redis, S3, et OCR.

## ℹ️ Fonctionnement

Le fonctionne de l'application est décrit dans les schémas suivant :

<img src= "docs/Diagrame.drawio.png" title="qsqs"></img>

En termes d'ordre d'execution :

```mermaid
flowchart TD
    A[Client envoie un document image/pdf] --> B[API Python reçoit le fichier]
    B --> C[Le fichier est sauvegardé dans S3]
    C --> D[Création de la task en BDD -task_id, status = CREATED]
    D --> E[Envoi de la task dans la queue du Broker]
    E --> F[Queue FIFO Broker]
    F --> G[Consommateur OCR récupère une tâche - pas de doublon]
    G --> H[Récupération du fichier depuis S3]
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

La diagramme de séquence est le suivant :

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant S3
    participant BDD
    participant Broker
    participant Consommateur_OCR

    Client->>API: Envoi document (image/pdf)
    API->>S3: Sauvegarde du fichier
    API->>BDD: Création task (task_id, status=CREATED)
    API->>Broker: Push task dans la queue
    Broker->>Consommateur_OCR: Délivre task (FIFO, sans doublon)
    Consommateur_OCR->>S3: Récupération du fichier
    Consommateur_OCR->>BDD: Maj status étape par étape (processing...)
    Client->>API: Demande status task
    API->>BDD: Lecture status task
    API-->>Client: Retour état + résultats si dispo

```

## 🛟 Contribution

Le projet utilise les prérequis suivant :

- Linux ou macOS
- `Docker` et `Docker Compose`
- `curl`, `make`

L'ensemble des commandes du projet est disponible avec la commande

```
make
```

### ⚙️ Installation

Installation des dépendances Python depuis `pyproject.toml` :

```bash
# with pip
pip install -r requirements.txt

# with docker
docker build -t ocr-api .
```

## Run
```bash
# with python
uvicorn main:app --reload --host 0.0.0.0 --port 5000

# with docker
docker run --rm -p 5000:5000 -v $PWD:/app ocr-api

#With docker compose
docker compose -f docker-compose.yaml up -d
```


then open `localhost:5000`

## Test
Use file `test.py` or write some code:
```python
import requests
import base64


with open("image_test.jpg", "rb") as image_file:
    encoded_data = base64.b64encode(image_file.read()).decode()

res = requests.post(
                    url='http://localhost:5000/',
                    json={"images": [encoded_data]}).json()
print("-------",res['msg'])
print(res['results'])
print("\n\n")
```

### With pytest
```
docker compose -f docker-compose.yaml run backend /bin/sh -c 'pip3 install pytest && pytest tests/ -s'
```

## Frontend

### Installation

Utilisation d'un Makefile pour exécuter les commandes ***(installation de `make` requis)***.


```sh
# Démarrer l'environnement de développement
make up-frontend

# Démarrer & mettre à jour les types
make generate-openapi
```
