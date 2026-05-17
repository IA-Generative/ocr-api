# Documentation OCR

Cette section contient des informations détaillées sur le fonctionnement et l'utilisation des fonctionnalités OCR de l'API et du frontend.

## Frontend

![ocr-main](../images/ocr/ocr-simple.png)



### Description des fonctionnalités du frontend

- **Masquer l'image** : Permet de masquer l'image et de garder les bounding boxes visibles avec leur texte.
- **Annoter une zone** : Cette fonctionnalité permet d'annoter une zone si le modèle n'a pas trouvé de résultat. Pour annoter, cliquez sur le bouton, puis effectuez une sélection rectangulaire. Une modal s'affichera avec la zone sélectionnée, où vous pourrez remplir le texte voulu et valider.
- **Métriques** : Permet de savoir, pour ce document, à quel point le modèle est performant grâce aux retours utilisateur.
- **Voir le texte** : Affiche le contenu total du texte brut extrait.
- **Aide** : Fournit un tutoriel étape par étape pour chaque fonctionnalité mentionnée.
- **Télécharger** : Permet de télécharger le texte extrait au format `.txt`.
- **Barre de recherche** : Une barre de recherche est disponible pour parcourir les bounding boxes. Lorsqu'une bounding box est sélectionnée dans les résultats de recherche, l'affichage pointe directement vers cette bounding box dans l'image.

- **Onglet Layout** : Cet onglet offre une vue détaillée de la mise en page du document. En cliquant sur une des mises en page, une image et les détails correspondants sont affichés :
  - Si la mise en page est une image, un descriptif est généré (si la variable `OPENAI_VISION_MODEL` est activée).
  - Si la mise en page est un tableau, celui-ci est présenté dans un format tableau Markdown et également disponible en JSON copiable.

---
![ocr-bbox](../images/ocr/ocr-bbox-prediction.png)

- **Modifier une bounding box** : Lorsqu'une bounding box est sélectionnée, une image recadrée (crop) de la zone est affichée. L'utilisateur peut copier le texte extrait, le modifier si le modèle a fait une erreur, et indiquer si les données sont publiques ou privées (avec une option pour les cacher dans le cadre d'un réentraînement). De plus, l'utilisateur peut évaluer la détection comme valide ou invalide pour donner son avis sur la qualité.

--- 


## API

### Fonctionnalités

- Extraction de texte à partir d'images et de PDF.
- Support multilingue grâce à PaddleOCR.
- Traitement asynchrone pour des performances optimales.

### Utilisation

Pour utiliser les fonctionnalités OCR, envoyez une requête POST à l'endpoint `/api/v1/jobs` avec le fichier à traiter.

Exemple :

```bash
curl -X POST "http://localhost:5000/api/v1/jobs" \
  -F "file=@/chemin/vers/fichier.pdf"
```

### Réponse

La réponse contiendra un objet conforme au schéma `Task` avec les résultats OCR dans le champ `output` (voir [`OCRResult`](../../apps/server/src/schemas/output.py)).

Exemple :

```json
{
  "id": "12345",
  "user_id": "user_1",
  "status": "completed",
  "output": {
    "text": "Texte extrait...",
    "metadata": {
      "language": "fr",
      "confidence": 0.98
    }
  }
}
```

### Récupération du statut et des résultats

Pour suivre l'état d'une tâche et récupérer les résultats, utilisez l'endpoint `/api/tasks/{task_id}`. Cet endpoint retourne un objet conforme au schéma `Task`.

#### Exemple de requête

```bash
curl -X GET "http://localhost:5000/api/tasks/12345"
```

#### Exemple de réponse

```json
{
  "id": "12345",
  "user_id": "user_1",
  "status": "completed",
  "output": {
    "text": "Texte extrait...",
    "metadata": {
      "language": "fr",
      "confidence": 0.98
    }
  }
}
```

#### Champs importants

- `status` : Indique l'état actuel de la tâche (ex. `queued`, `in_progress`, `completed`, etc.).
- `output` : Contient les résultats OCR lorsque la tâche est terminée avec succès (voir [`OCRResult`](../../apps/server/src/schemas/output.py)).