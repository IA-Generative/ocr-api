# Exemples de commandes curl pour l’API OCR

```bash
# Variables à adapter
BASE_URL="http://localhost:5000/api"
TOKEN="votre_token"
TASK_ID="votre_task_id"
FICHIER="/chemin/vers/votre/fichier.jpg"
```

## 1. Créer une tâche (upload d’un fichier)

```bash
curl -X POST "$BASE_URL/jobs/" \
  -H "accept: application/json" \
  -F "file=@$FICHIER" \
  -F "group_id=DEFAULT" \
  -F "task_operation=ocr" | jq
```

## 2. Récupérer une tâche par son ID

```bash
curl -X GET "$BASE_URL/tasks/$TASK_ID" \
  -H "accept: application/json" \
  -H "Authorization: Bearer $TOKEN" | jq
```

## 3. Récupérer toutes les tâches d’un utilisateur

```bash
curl -X GET "$BASE_URL/tasks/user/?page=1&page_size=10" \
  -H "accept: application/json" \
  -H "Authorization: Bearer $TOKEN" | jq
```

## 4. Supprimer des tâches (exemple avancé avec filtres)

```bash
curl -X DELETE "$BASE_URL/v1/tasks/" \
  -H "x-user-id: test-user-id" \
  -H "x-user-email: test@example.com" \
  -H "x-roles: admin,user" \
  -H "authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -G \
  --data-urlencode "start_date=2024-08-01T00:00:00" \
  --data-urlencode "end_date=2025-08-06T23:59:59" \
  --data-urlencode "status=failed"
```

## 5. Télécharger le texte d’une tâche

```bash
curl -X GET "$BASE_URL/text-task/$TASK_ID" \
  -H "accept: text/plain" \
  -H "Authorization: Bearer $TOKEN"
```

## 6. Télécharger les résultats d’une tâche sous différents formats

```bash
# Texte brut
curl -X GET "$BASE_URL/task-to-value/$TASK_ID?transform=text" \
  -H "accept: text/plain" \
  -H "Authorization: Bearer $TOKEN"

# Résultat brut (JSON)
curl -X GET "$BASE_URL/task-to-value/$TASK_ID?transform=only-result" \
  -H "accept: application/json" \
  -H "Authorization: Bearer $TOKEN" | jq

# Formulaires (JSON)
curl -X GET "$BASE_URL/task-to-value/$TASK_ID?transform=form" \
  -H "accept: application/json" \
  -H "Authorization: Bearer $TOKEN" | jq

# Formulaires (CSV)
curl -X GET "$BASE_URL/task-to-value/$TASK_ID?transform=form-csv" \
  -H "accept: text/csv" \
  -H "Authorization: Bearer $TOKEN" -OJ
```

## 7. Vérifier la santé de l’API

```bash
curl -X GET "$BASE_URL/health" \
  -H "accept: application/json" | jq
```

---

**Astuce :**
Ajoute `| jq` à la fin de chaque commande pour un affichage plus lisible des résultats JSON.
