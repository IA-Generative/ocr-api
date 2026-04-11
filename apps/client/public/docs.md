# OCR API — Documentation

## Authentification

Toutes les routes (sauf `/api/health`) nécessitent un token dans l'en-tête HTTP :

```
Authorization: Bearer <VOTRE_TOKEN>
```

Générez un token via la modal **Générer un token** accessible depuis la barre de navigation.

---

## Soumettre un fichier

### `POST /api/jobs/`

Soumet un fichier (image ou PDF) à la file de traitement OCR.

| Paramètre | Type | Obligatoire | Description |
|---|---|---|---|
| `file` | `File` | ✅ | Fichier image (`image/*`) ou PDF (`application/pdf`) |
| `group_id` | `string` | — | Identifiant de groupe (défaut : `DEFAULT`) |
| `interest_zone` | `string` (JSON) | — | Zone d'intérêt, tableau de régions (une par page pour un PDF) |
| `task_operation` | `string` | — | Type d'opération (défaut : `DEFAULT`) |

**Réponse `201`** — objet `TaskModel` avec l'`id` de la tâche créée.

```bash
curl -X POST \
  -H "Authorization: Bearer <VOTRE_TOKEN>" \
  -F "file=@document.pdf" \
  -F "group_id=mon-groupe" \
  http://localhost:5000/api/jobs/
```

```python
import requests

with open("document.pdf", "rb") as f:
    resp = requests.post(
        "http://localhost:5000/api/jobs/",
        headers={"Authorization": "Bearer <VOTRE_TOKEN>"},
        files={"file": f},
        data={"group_id": "mon-groupe"},
    )

task = resp.json()
print(task["id"])  # ex: "3f2a1b..."
```

---

## Suivre une tâche

### `GET /api/tasks/{task_id}`

Retourne l'état et le résultat d'une tâche.

| Champ | Description |
|---|---|
| `status` | `CREATED` · `QUEUED` · `PROCESSING` · `COMPLETED` · `FAILED` |
| `percentage` | Avancement de 0 à 100 |
| `output.text` | Texte extrait (disponible si `COMPLETED`) |
| `output.pages` | Détail par page avec URL d'aperçu et bounding boxes |
| `position` | Position dans la file d'attente |

```bash
curl -H "Authorization: Bearer <VOTRE_TOKEN>" \
  http://localhost:5000/api/tasks/3f2a1b...
```

### `GET /api/tasks/user/`

Liste paginée des tâches de l'utilisateur courant.

| Query param | Défaut | Description |
|---|---|---|
| `page` | `1` | Numéro de page |
| `page_size` | `10` | Taille de page (max `100`) |

---

## Récupérer le texte extrait

### `GET /api/text-task/{task_id}`

Retourne le texte extrait brut (`text/plain`).

### `GET /api/task-to-value/{task_id}`

Retourne le résultat dans différents formats selon le paramètre `transform` :

| Valeur | Description |
|---|---|
| `text` | Texte brut (défaut) |
| `form` | Entrées de formulaire détectées, par page |
| `form-csv` | Entrées de formulaire au format CSV |
| `only-result` | Objet `output` complet (JSON) |

---

## Annotations

Les annotations permettent d'associer des métadonnées à un fichier identifié par son hash de contenu.

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/api/annotations/{content_hash}` | Récupère l'annotation d'un fichier |
| `PUT` | `/api/annotations/{content_hash}` | Crée ou met à jour une annotation (upsert) |
| `DELETE` | `/api/annotations/{content_hash}` | Supprime une annotation (admin) |
| `GET` | `/api/annotations/user/` | Liste paginée des annotations de l'utilisateur |
| `GET` | `/api/stats/annotations` | Métriques globales et par utilisateur |

---

## OCR Chunks (recherche sémantique)

Les chunks permettent d'indexer des fragments vectorisés pour la recherche sémantique.

| Méthode | Route | Description |
|---|---|---|
| `POST` | `/api/ocr-chunks/{content_hash}` | Indexe (upsert) un lot de chunks vectorisés |
| `GET` | `/api/ocr-chunks/{content_hash}` | Liste tous les chunks d'un fichier |
| `POST` | `/api/ocr-chunks/{content_hash}/search` | Recherche sémantique sur les chunks d'un fichier |
| `DELETE` | `/api/ocr-chunks/{content_hash}` | Supprime tous les chunks d'un fichier |

**Exemple de recherche sémantique :**

```python
import requests

resp = requests.post(
    "http://localhost:5000/api/ocr-chunks/abc123.../search",
    headers={"Authorization": "Bearer <VOTRE_TOKEN>"},
    json={"query_vector": [0.1, 0.2, ...], "top_k": 5},
)
print(resp.json())  # liste de chunks avec page_num et bbox_indices
```

---

## Chat (compatible OpenAI)

### `POST /api/v1/chat/completions`

Interface compatible OpenAI Chat Completions. Accepte un fichier ou une image dans les messages pour en extraire le contenu via OCR avant de générer une réponse.

```python
import requests

resp = requests.post(
    "http://localhost:5000/api/v1/chat/completions",
    headers={"Authorization": "Bearer <VOTRE_TOKEN>"},
    json={
        "model": "ocr-v1",
        "messages": [
            {"role": "user", "content": "Extrais le texte de cette image"},
        ],
    },
)
print(resp.json()["choices"][0]["message"]["content"])
```

Supporte le **streaming** (`"stream": true`) avec des événements Server-Sent Events (SSE).

### `GET /api/v1/models`

Liste les modèles OCR disponibles (format compatible OpenAI).

---

## Tokens

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/api/v1/tokens/` | Liste les tokens de l'utilisateur courant |
| `POST` | `/api/v1/tokens/` | Crée un nouveau token |
| `DELETE` | `/api/v1/tokens/{token_id}` | Supprime un token |

---

## Santé

### `GET /api/health`

Vérifie l'état de toutes les dépendances (base de données, Redis, S3). Ne nécessite pas d'authentification.

```bash
curl http://localhost:5000/api/health
```

**Réponse `200` (healthy) ou `503` (unhealthy) :**

```json
{
  "name": "ocr-api",
  "version": "1.0.0",
  "status": "healthy",
  "dependencies": [
    {"name": "db", "status": "healthy"},
    {"name": "redis", "status": "healthy"},
    {"name": "s3", "status": "healthy"}
  ]
}
```

---

## Statistiques

| Route | Description |
|---|---|
| `GET /api/stats/tasks` | Statistiques des tâches (admin : global, utilisateur : restreint) |
| `GET /api/stats/annotations` | Métriques des annotations |
| `GET /api/users/count-users-today` | Nombre d'utilisateurs distincts ayant soumis une tâche aujourd'hui |
