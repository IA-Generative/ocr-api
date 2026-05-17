# OCR API
## Introduction

OCR API est une solution complète pour extraire du texte à partir de fichiers PDF ou d’images. Elle utilise des technologies avancées comme PaddleOCR et un pipeline asynchrone pour offrir des résultats rapides et précis. Cette API est conçue pour être facilement intégrée dans vos projets grâce à son SDK Python et ses fonctionnalités robustes.

![Démo](docs/images/demo-ocr.gif)

---

## Table des matières

- [Introduction](#introduction)
- Fonctionnalités disponibles
  - [OCR](docs/ocr/README.md)
  - [Classification](docs/classification/README.md)
  - [Extractions d'entités](docs/extractions/README.md)
  - [Templates](docs/templates/README.md)
- [Installation](docs/server/INSTALL.md)
- [Usage](docs/server/USAGE.md)

---

## Fonctionnement Asynchrone

<div align="center">

```mermaid
graph TD
    A[Client] -->|Request| B[API Gateway]
    B -->|Forward| C[OCR Service]
    C -->|Process| D[Database]
    C -->|Store| E[MinIO]
    D -->|Retrieve| F[Result Formatter]
    E -->|Retrieve| F
    F -->|Response| A
```

</div>

Ce diagramme illustre le fonctionnement asynchrone de l'application, mettant en évidence les interactions entre les différents composants.

