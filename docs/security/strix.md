# Strix Security Scan (CI/CD)

Ce workflow ([security-strix.yml](../../.github/workflows/security-strix.yml)) intègre [Strix](https://github.com/usestrix/strix), un agent IA de pentest autonome, à la CI GitHub Actions.

## Fonctionnement

Strix exécute le code dynamiquement (dans un sandbox conteneurisé), recherche des vulnérabilités et les valide via des preuves de concept réelles. Il se déclenche :

- automatiquement sur les pull requests (ouverture, réouverture, synchronisation, sortie de brouillon) ;
- manuellement via `workflow_dispatch`.

Le job est ignoré si la PR est en brouillon.

## Configuration requise

Le workflow attend un LLM pour piloter l'agent. Ajoute les secrets suivants dans **Settings → Secrets and variables → Actions** du repository :

| Secret               | Requis | Description                                                          |
|----------------------|--------|----------------------------------------------------------------------|
| `STRIX_LLM`          | Oui    | Modèle à utiliser, ex. `openai/gpt-5.4`, `anthropic/claude-sonnet-5` |
| `LLM_API_KEY`        | Oui    | Clé API du fournisseur LLM                                           |
| `LLM_API_BASE`       | Non    | URL de base pour un modèle auto-hébergé (décommenter dans le YAML)   |
| `PERPLEXITY_API_KEY` | Non    | Clé pour activer la recherche web pendant le scan (décommenter)      |

## Personnalisation

- `--scan-mode quick` peut être remplacé par un autre mode (voir `strix --help`) pour un scan plus approfondi.
- Le ciblage `-t ./` scanne l'ensemble du dépôt ; on peut cibler un sous-dossier (ex. `apps/server`) ou une URL déployée.
- `-n` lance Strix en mode headless (sans dashboard interactif), adapté à la CI.

## Documentation

Voir le [dépôt officiel Strix](https://github.com/usestrix/strix) pour la liste complète des options CLI et des fournisseurs LLM supportés.
