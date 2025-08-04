# Exploration de PaddleOCR 3.1.0

Ce dossier contient une exploration de la bibliothèque [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR), version **3.1.0**.

## Objectif

Tester les performances, la facilité d’utilisation et les capacités de PaddleOCR v3.1.0 pour la reconnaissance optique de caractères (OCR) sur divers jeux de données.

## Contenu

- `apps/server/tests/data/valid/` : quelques images utilisées pour les tests.
- `results/` : sorties OCR générées par PaddleOCR (texte extrait, images annotées, etc.).
- `notes.md` : observations, problèmes rencontrés, améliorations potentielles.

## Environnement utilisé

- Python 3.x
- PaddleOCR 3.1.0
- PaddlePaddle (backend requis)
- Autres dépendances : voir `requirements.txt` si présent

## Commandes utiles

Installation rapide :

```bash
pip install paddleocr==3.1.0
pip install paddlepaddle  # ou paddlepaddle-gpu si nécessaire
```

## Résultats / Observations

- [x] Facile à installer
- [x] Support multilingue efficace
- [ ] Peut ralentir sur des images très larges
- [ ] Besoin d’un bon prétraitement pour certaines images bruitées

## Remarques

Cette exploration vise uniquement à évaluer PaddleOCR **dans un contexte expérimental**. Elle ne représente pas un choix définitif pour un pipeline de production.
