# Métriques d'évaluation pour la classification KNN avec FAISS

Ce document décrit les différentes métriques utilisées pour évaluer les performances de notre système de classification basé sur KNN (K-Nearest Neighbors) avec FAISS.

## Métriques de recherche

### Top-K Accuracy

- **Description** : Pourcentage de cas où la classe correcte se trouve parmi les K premiers résultats
- **Formule** : `(Nombre de prédictions correctes dans les K premiers) / (Nombre total de prédictions)`
- **Usage** : Évalue la qualité du ranking des résultats
- **Valeurs typiques** : K = 1, 3, 5, 10

### Mean Reciprocal Rank (MRR)

- **Description** : Moyenne de l'inverse du rang du premier résultat correct
- **Formule** : `MRR = (1/N) * Σ(1/rank_i)` où rank_i est le rang du premier résultat correct pour la requête i
- **Usage** : Mesure la qualité du classement en pénalisant les bonnes réponses mal classées
- **Plage** : [0, 1], plus c'est proche de 1, mieux c'est

## Métriques de classification

### Accuracy (Exactitude)

- **Description** : Proportion de prédictions correctes sur l'ensemble des prédictions
- **Formule** : `(TP + TN) / (TP + TN + FP + FN)`
- **Usage** : Métrique globale de performance
- **Limitations** : Peut être trompeuse sur des datasets déséquilibrés

### Precision (Précision)

- **Description** : Proportion de vrais positifs parmi les prédictions positives
- **Formule** : `TP / (TP + FP)`
- **Usage** : Mesure la qualité des prédictions positives
- **Interprétation** : Répond à "Parmi les éléments classés comme positifs, combien le sont réellement ?"

### Recall (Rappel/Sensibilité)

- **Description** : Proportion de vrais positifs détectés parmi tous les vrais positifs
- **Formule** : `TP / (TP + FN)`
- **Usage** : Mesure la capacité à détecter les cas positifs
- **Interprétation** : Répond à "Parmi tous les éléments positifs, combien ont été détectés ?"

### F1-Score

- **Description** : Moyenne harmonique de la précision et du rappel
- **Formule** : `2 * (Precision * Recall) / (Precision + Recall)`
- **Usage** : Équilibre entre précision et rappel
- **Avantage** : Une seule métrique qui combine précision et rappel

## Métriques spécifiques à FAISS

### Distance moyenne

- **Description** : Distance euclidienne ou cosinus moyenne entre la requête et les voisins trouvés
- **Usage** : Évalue la qualité de l'espace de représentation
- **Interprétation** : Plus la distance est faible, plus les voisins sont similaires

### Temps de recherche

- **Description** : Temps moyen pour effectuer une recherche KNN
- **Unité** : Millisecondes ou microsecondes
- **Usage** : Évalue l'efficacité computationnelle
- **Facteurs** : Taille de l'index, type d'index, valeur de K

### Recall@K pour la recherche

- **Description** : Proportion des vrais voisins présents dans les K premiers résultats
- **Usage** : Évalue la qualité de l'approximation (pour les index approximatifs)
- **Formule** : `|vrais_voisins ∩ voisins_trouvés| / |vrais_voisins|`

## Métriques multi-classes

### Macro-averaged metrics

- **Description** : Moyenne des métriques calculées pour chaque classe indépendamment
- **Usage** : Traite toutes les classes de manière égale
- **Formule** : `(métrique_classe1 + métrique_classe2 + ... + métrique_classeN) / N`

### Micro-averaged metrics

- **Description** : Métriques calculées globalement en agrégeant les TP, FP, FN de toutes les classes
- **Usage** : Favorise les classes avec plus d'exemples
- **Formule** : `TP_total / (TP_total + FP_total)` pour la précision micro

### Weighted-averaged metrics

- **Description** : Moyenne pondérée des métriques par classe selon le nombre d'exemples
- **Usage** : Compromis entre macro et micro averaging

## Matrice de confusion

### Description

Tableau de contingence montrant les prédictions vs les vraies classes

### Utilité

- Visualise les erreurs de classification
- Identifie les classes souvent confondues
- Aide à comprendre les biais du modèle

## Configuration recommandée

```python
# Exemple de métriques à calculer
metrics_config = {
    "top_k_values": [1, 3, 5, 10],
    "distance_metrics": ["euclidean", "cosine"],
    "classification_metrics": [
        "accuracy",
        "precision_macro",
        "recall_macro",
        "f1_macro",
        "precision_micro",
        "recall_micro",
        "f1_micro"
    ],
    "search_metrics": ["mrr", "recall_at_k"],
    "performance_metrics": ["search_time", "memory_usage"]
}
```

## Notes d'implémentation

- Utiliser `sklearn.metrics` pour les métriques de classification classiques
- Implémenter des métriques custom pour MRR et Top-K accuracy
- Mesurer les performances avec `time.perf_counter()` pour la précision
- Sauvegarder les résultats dans des formats structurés (JSON, CSV) pour analyse
