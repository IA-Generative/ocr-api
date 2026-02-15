# Guide de Démarrage Rapide - OCR SDK JavaScript

Ce guide vous aidera à commencer rapidement avec le SDK OCR JavaScript.

## Installation Rapide

1. **Naviguez vers le dossier sdk-js**:
   ```bash
   cd sdk-js
   ```

2. **Installez les dépendances**:
   ```bash
   npm install
   ```

3. **Compilez le SDK** (si vous modifiez le code source):
   ```bash
   npm run build
   ```

## Premier Exemple

Créez un fichier `test.js` ou `test.ts`:

```typescript
import { SyncOCRClient, TaskOperation } from "@ia-generative/ocr-sdk";

async function quickTest() {
  // Créer le client
  const client = new SyncOCRClient({
    baseUrl: "http://localhost:5000"
  });

  try {
    // Vérifier que l'API fonctionne
    const health = await client.getHealth();
    console.log("API Status:", health.status);

    // Traiter un document
    const task = await client.createJob(
      "path/to/your/document.pdf",
      "DEFAULT",
      undefined,
      TaskOperation.DEFAULT
    );
    console.log("Task ID:", task.id);

    // Attendre le résultat
    const result = await client.waitForTask(task.id);
    console.log("Status:", result.status);

    // Récupérer le texte
    const text = await client.getTaskText(task.id);
    console.log("Texte extrait:", text.substring(0, 100) + "...");
  } catch (error) {
    console.error("Erreur:", error.message);
  }
}

quickTest();
```

## Méthode Simplifiée

Pour traiter un document en une seule étape:

```typescript
import { SyncOCRClient, TaskOperation } from "@ia-generative/ocr-sdk";

async function processFile() {
  const client = new SyncOCRClient({
    baseUrl: "http://localhost:5000"
  });

  const results = await client.processDocument(
    "path/to/document.pdf",
    "DEFAULT",
    TaskOperation.DEFAULT
  );

  results.forEach((page) => {
    console.log(`Page ${page.metadata.page_number}:`, page.page_content);
  });
}

processFile();
```

## Exécution

### Avec TypeScript (ts-node)

```bash
npx ts-node test.ts
```

### Avec JavaScript (après build)

```bash
npm run build
node test.js
```

## Prochaines Étapes

- Consultez le [README.md](./README.md) pour la documentation complète
- Explorez les exemples dans le dossier `examples/`
- Lisez la référence API pour toutes les méthodes disponibles

## Ressources

- **Python SDK**: Voir `../sdk/` pour comparer avec l'implémentation Python
- **API Documentation**: Consultez la documentation de l'API OCR pour plus de détails
- **Examples**: Dossier `examples/` pour des cas d'usage complets

## Besoin d'Aide ?

Si vous rencontrez des problèmes:

1. Vérifiez que l'API OCR est démarrée et accessible
2. Vérifiez que le chemin vers votre fichier est correct
3. Vérifiez les logs d'erreur pour plus de détails
4. Consultez les exemples pour voir des cas d'usage fonctionnels
