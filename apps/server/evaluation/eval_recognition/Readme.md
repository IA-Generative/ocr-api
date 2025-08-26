# Évaluation OCR – Description des métriques

Ce module propose plusieurs métriques pour évaluer la qualité de la reconnaissance de texte (OCR) sur des documents, en utilisant le dataset [pixparse/pdfa-eng-wds](https://huggingface.co/datasets/pixparse/pdfa-eng-wds).

## Dataset utilisé

- **Nom** : [pixparse/pdfa-eng-wds](https://huggingface.co/datasets/pixparse/pdfa-eng-wds)
- **Source** : Hugging Face
- **Description** : Ce dataset contient des documents PDF annotés pour l’évaluation de modèles OCR.

## Métriques disponibles

Les fonctions du fichier `metrics.py` permettent de calculer les métriques suivantes :

- **CER (Character Error Rate)**
  Taux d’erreur sur les caractères. Plus il est bas, meilleure est la reconnaissance.
  Calculé avec `jiwer.cer`.

- **WER (Word Error Rate)**
  Taux d’erreur sur les mots. Plus il est bas, meilleure est la reconnaissance.
  Calculé avec `jiwer.wer`.

- **IoU Text (Intersection over Union)**
  Mesure le recouvrement entre les mots de la référence et de l’hypothèse (intersection sur union des ensembles de mots).

- **Presence Words**
  Mesure la proportion de mots de la référence retrouvés dans l’hypothèse, pondérée par la longueur totale.

- **Precision**
  Proportion de mots de l’hypothèse présents dans la référence.

- **Recall**
  Proportion de mots de la référence retrouvés dans l’hypothèse.

- **F1-score**
  Moyenne harmonique entre la précision et le rappel, pour évaluer l’équilibre entre les deux.

## Utilisation

Ces métriques sont à utiliser pour comparer les textes reconnus par un modèle OCR avec les textes de référence du dataset, afin de quantifier la qualité de la reconnaissance.

---
Pour plus de détails, voir le fichier [`metrics.py`](./metrics.py).
