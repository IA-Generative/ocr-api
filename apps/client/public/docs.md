# OCR API — Documentation

## Authentification

Toutes les routes (sauf `/api/health`) nécessitent un token dans l'en-tête HTTP :

```
Authorization: Bearer <VOTRE_TOKEN>
```

Gérez vos tokens via la modal **Générer un token** accessible depuis la barre de navigation, ou via les routes [Tokens](#tokens).

---

## Soumettre un fichier

### `POST /api/jobs/`

Soumet un fichier à la file de traitement.

| Paramètre | Type | Obligatoire | Description |
|---|---|---|---|
| `file` | `File` | ✅ | Fichier image (`image/*`) ou PDF (`application/pdf`) |
| `group_id` | `string` (form) | — | Identifiant de groupe (défaut : `DEFAULT`) |
| `task_operation` | `string` (form) | — | Type d'opération (voir ci-dessous, défaut : `default`) |
| `task_name` | `string` (form) | — | Nom de la tâche Celery (défaut : `worker.tasks.ocr`) |
| `parameter` | `string` JSON (form) | — | Paramètres supplémentaires selon l'opération |
| `interest_zone` | `string` JSON (form) | — | Zone d'intérêt — tableau de régions (une par page PDF, une pour une image) |

**Valeurs de `task_operation` :**

| Valeur | Description |
|---|---|
| `default` / `ocr` | Extraction de texte OCR classique |
| `forms` | Extraction des entrées de formulaire |
| `vectorize` | Vectorisation du contenu extrait |
| `vlm_ocr` | OCR assisté par un modèle de vision (VLM) |
| `page_classification` | Classification de pages par type de document *(expérimental)* |
| `save_template` | Sauvegarde d'un template |

**Réponse `201`** — objet `TaskModel` avec l'`id` de la tâche créée.

```bash
curl -X POST \
  -H "Authorization: Bearer <VOTRE_TOKEN>" \
  -F "file=@document.pdf" \
  -F "group_id=mon-groupe" \
  -F "task_operation=ocr" \
  http://localhost:5000/api/jobs/
```

```python
import requests

with open("document.pdf", "rb") as f:
    resp = requests.post(
        "http://localhost:5000/api/jobs/",
        headers={"Authorization": "Bearer <VOTRE_TOKEN>"},
        files={"file": f},
        data={"group_id": "mon-groupe", "task_operation": "ocr"},
    )

task = resp.json()
print(task["id"])  # ex: "3f2a1b..."
```

---

## Tâches

### `GET /api/tasks/{task_id}`

Retourne l'état et le résultat d'une tâche. Les URLs de pages (`page_url`) sont des URLs présignées valables **5 minutes**.

| Champ | Description |
|---|---|
| `status` | `created` · `queued` · `in_progress` · `completed` · `failed` · `retrying` · `canceled` · `timeout` |
| `percentage` | Avancement de 0 à 1 |
| `output.text` | Texte extrait (disponible si `completed`) |
| `output.pages` | Détail par page avec URL d'aperçu et bounding boxes |
| `position` | Position dans la file d'attente (si `queued`) |

> Les pages de `output` ne sont retournées que si le statut est `completed`.

```bash
curl -H "Authorization: Bearer <VOTRE_TOKEN>" \
  http://localhost:5000/api/tasks/3f2a1b...
```

### `GET /api/tasks/content/{content_hash}`

Récupère une tâche par le hash du contenu du fichier soumis.

### `GET /api/tasks/user/`

Liste paginée des tâches de l'utilisateur courant.

| Query param | Défaut | Description |
|---|---|---|
| `page` | `1` | Numéro de page (≥ 1) |
| `page_size` | `10` | Taille de page (max `100`) |

### `PATCH /api/tasks/{task_id}`

Met à jour une tâche. Requiert le query param `task_type` (valeur de `task_operation`).

### `GET /api/stats/tasks`

Statistiques des tâches. Retourne les données globales pour les admins, restreintes à l'utilisateur sinon.

---

## Récupérer le texte extrait

### `GET /api/text-task/{task_id}`

Retourne le texte extrait brut (`text/plain`).

| Query param | Défaut | Description |
|---|---|---|
| `task_type` | `ocr` | Type de l'opération |

### `GET /api/task-to-value/{task_id}`

Retourne le résultat dans différents formats.

| Query param `transform` | Description |
|---|---|
| `text` *(défaut)* | Texte brut |
| `form` | Entrées de formulaire détectées, par page |
| `form-csv` | Entrées de formulaire au format CSV |
| `only-result` | Objet `output` complet (JSON) |

---

## Annotations

Les annotations associent des métadonnées à un fichier identifié par son hash de contenu.

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/api/annotations/{content_hash}` | Récupère l'annotation (admin : sans restriction de propriétaire) |
| `PUT` | `/api/annotations/{content_hash}` | Crée ou met à jour une annotation (upsert) |
| `DELETE` | `/api/annotations/{content_hash}` | Supprime une annotation *(admin uniquement)* |
| `GET` | `/api/annotations/user/` | Liste paginée des annotations de l'utilisateur (`page`, `page_size`) |

---

## OCR Chunks (recherche sémantique)

Indexation et recherche sur des fragments vectorisés issus de l'OCR.

| Méthode | Route | Description |
|---|---|---|
| `POST` | `/api/ocr-chunks/{content_hash}` | Indexe (upsert) un lot de chunks vectorisés |
| `GET` | `/api/ocr-chunks/{content_hash}` | Liste tous les chunks d'un fichier |
| `POST` | `/api/ocr-chunks/{content_hash}/search` | Recherche sémantique (top-k) sur les chunks d'un fichier |
| `DELETE` | `/api/ocr-chunks/{content_hash}` | Supprime tous les chunks d'un fichier |

Chaque chunk contient : `page_num`, `bbox_indices`, `text`, `model_name`, `vector`, `vector_size`.

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

Supporte le **streaming** (`"stream": true`) via Server-Sent Events (SSE).

```python
import requests

resp = requests.post(
    "http://localhost:5000/api/v1/chat/completions",
    headers={"Authorization": "Bearer <VOTRE_TOKEN>"},
    json={
        "model": "ocr-v1",
        "messages": [{"role": "user", "content": "Extrais le texte de cette image"}],
    },
)
print(resp.json()["choices"][0]["message"]["content"])
```

### `GET /api/v1/models`

Liste les modèles OCR disponibles (format compatible OpenAI).

---

## Tokens

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/api/v1/tokens/` | Liste les tokens de l'utilisateur courant |
| `POST` | `/api/v1/tokens/` | Crée un nouveau token |
| `DELETE` | `/api/v1/tokens/{token_id}` | Supprime un token (propriétaire uniquement) |

---

## Santé

### `GET /api/health`

Vérifie l'état de toutes les dépendances. Ne nécessite pas d'authentification.

**Réponse `200`** (healthy) ou **`503`** (unhealthy) :

```json
{
  "name": "ocr-api",
  "version": "1.1.1",
  "status": "healthy",
  "dependencies": [
    { "name": "db", "status": "healthy" },
    { "name": "redis", "status": "healthy" },
    { "name": "s3", "status": "healthy" }
  ]
}
```
