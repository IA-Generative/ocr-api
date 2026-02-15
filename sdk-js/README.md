# OCR SDK - JavaScript/TypeScript

SDK JavaScript/TypeScript pour interagir avec l'API OCR. Fournit un client avec des types TypeScript pour toutes les entrées et sorties.

## Installation

Avec npm:

```bash
cd sdk-js
npm install
```

Avec yarn:

```bash
cd sdk-js
yarn install
```

Avec pnpm:

```bash
cd sdk-js
pnpm install
```

## Fonctionnalités

- ✅ Client **asynchrone** avec axios
- ✅ Types **TypeScript** pour toutes les entrées/sorties
- ✅ Gestion des erreurs avec exceptions personnalisées
- ✅ Support de l'authentification par token
- ✅ Méthodes utilitaires (waitForTask, processDocument)
- ✅ Support ESM (ECMAScript Modules)

## Build

Pour compiler le SDK en JavaScript:

```bash
npm run build
```

Cela générera les fichiers JavaScript et les déclarations TypeScript dans le dossier `dist/`.

## Utilisation

### Client de Base

```typescript
import { SyncOCRClient, TaskOperation } from "@ia-generative/ocr-sdk";

// Créer une instance du client
const client = new SyncOCRClient({
  baseUrl: "http://localhost:5000",
  // apiKey: "your-api-key", // Optionnel: pour l'authentification
  timeout: 30000, // Optionnel: timeout en millisecondes (défaut: 30000)
});

// Vérifier l'état de santé de l'API
const health = await client.getHealth();
console.log(`API Status: ${health.status}`);

// Créer un job OCR
const task = await client.createJob(
  "path/to/document.pdf",
  "DEFAULT",
  undefined,
  TaskOperation.DEFAULT
);
console.log(`Task created: ${task.id}`);

// Attendre la fin du traitement
const completedTask = await client.waitForTask(task.id);

// Récupérer le texte extrait
if (completedTask.status === "completed") {
  const text = await client.getTaskText(task.id);
  console.log(`Extracted text: ${text}`);
}
```

### Traitement Direct avec processDocument

Pour une utilisation simplifiée, utilisez la méthode `processDocument` qui upload et attend le résultat automatiquement:

```typescript
import { SyncOCRClient, TaskOperation } from "@ia-generative/ocr-sdk";

const client = new SyncOCRClient({
  baseUrl: "http://localhost:5000"
});

// Traite le document et attend les résultats
const results = await client.processDocument(
  "path/to/document.pdf",
  "DEFAULT",
  TaskOperation.DEFAULT,
  2000,   // Intervalle de polling (ms)
  300000  // Temps d'attente max (ms)
);

results.forEach((result) => {
  console.log(`Page ${result.metadata.page_number}: ${result.page_content}`);
});
```

### Avec Authentification

```typescript
import { SyncOCRClient } from "@ia-generative/ocr-sdk";

// Fournir un token API
const client = new SyncOCRClient({
  baseUrl: "http://localhost:5000",
  apiKey: "your-api-token"
});

const health = await client.getHealth();
console.log(health);
```

### Récupérer les Tâches de l'Utilisateur

```typescript
import { SyncOCRClient } from "@ia-generative/ocr-sdk";

const client = new SyncOCRClient({
  baseUrl: "http://localhost:5000"
});

// Récupérer les tâches (pagination)
const tasks = await client.getUserTasks(1, 10); // page 1, 10 items per page

tasks.forEach((task) => {
  console.log(`Task ${task.id}: ${task.status}`);
});
```

## Types et Interfaces

Le SDK expose tous les types TypeScript nécessaires:

```typescript
import {
  TaskModel,      // Interface de tâche
  TaskStatus,     // Enum des statuts de tâche
  TaskOperation,  // Enum des types d'opération
  Health,         // Interface de santé API
  OCRResult,      // Résultat OCR
  Page,           // Page de document
  Bbox,           // Boîte englobante
} from "@ia-generative/ocr-sdk";
```

### Statuts de Tâche

```typescript
import { TaskStatus } from "@ia-generative/ocr-sdk";

// Statuts disponibles
TaskStatus.CREATED       // Tâche créée
TaskStatus.QUEUED        // En file d'attente
TaskStatus.STARTED       // Démarrée
TaskStatus.IN_PROGRESS   // En cours
TaskStatus.COMPLETED     // Terminée
TaskStatus.FAILED        // Échouée
TaskStatus.RETRYING      // Nouvelle tentative
TaskStatus.CANCELED      // Annulée
TaskStatus.TIMEOUT       // Timeout
```

### Types d'Opération

```typescript
import { TaskOperation } from "@ia-generative/ocr-sdk";

// Opérations disponibles
TaskOperation.DEFAULT         // Opération par défaut
TaskOperation.OCR            // OCR standard
TaskOperation.SAVE_TEMPLATE  // Sauvegarder comme template
TaskOperation.FORMS          // Extraction de formulaires
TaskOperation.VECTORIZE      // Vectorisation
TaskOperation.VLM_OCR        // OCR avec VLM
TaskOperation.DOCLING        // Traitement Docling
```

## Gestion des Erreurs

```typescript
import {
  SyncOCRClient,
  OCRAPIError,
  OCRTimeoutError,
  OCRAuthenticationError,
  OCRValidationError,
} from "@ia-generative/ocr-sdk";

const client = new SyncOCRClient({
  baseUrl: "http://localhost:5000"
});

try {
  const task = await client.createJob("document.pdf");
  const result = await client.waitForTask(task.id, 2000, 60000);
} catch (error) {
  if (error instanceof OCRTimeoutError) {
    console.error(`Timeout: ${error.message}`);
  } else if (error instanceof OCRAPIError) {
    console.error(`API Error ${error.statusCode}: ${error.responseMessage}`);
  } else if (error instanceof OCRAuthenticationError) {
    console.error(`Authentication failed: ${error.message}`);
  } else if (error instanceof OCRValidationError) {
    console.error(`Validation error: ${error.message}`);
  } else {
    console.error(`Unknown error: ${error}`);
  }
}
```

## Exemples

Le dossier `examples/` contient des exemples d'utilisation:

- `sync-example.ts` - Exemple complet avec toutes les opérations
- `process-document.ts` - Exemple de traitement de document simplifié

Pour exécuter les exemples (après avoir compilé le SDK):

```bash
npm run build
node examples/sync-example.js
```

Ou avec ts-node:

```bash
npx ts-node examples/sync-example.ts
```

## API Reference

### SyncOCRClient

#### Constructor

```typescript
new SyncOCRClient(options: OCRClientOptions)
```

Options:
- `baseUrl: string` - URL de base de l'API OCR (ex: "http://localhost:5000")
- `apiKey?: string` - Token API optionnel pour l'authentification
- `timeout?: number` - Timeout par défaut en millisecondes (défaut: 30000)

#### Methods

##### getHealth()

Récupère l'état de santé de l'API.

```typescript
async getHealth(): Promise<Health>
```

##### createJob()

Crée un nouveau job OCR.

```typescript
async createJob(
  filePath: string,
  groupId?: string,
  interestZone?: string,
  taskOperation?: TaskOperation
): Promise<TaskModel>
```

Paramètres:
- `filePath` - Chemin vers le fichier à traiter
- `groupId` - ID du groupe (défaut: "DEFAULT")
- `interestZone` - JSON string définissant les régions d'intérêt (optionnel)
- `taskOperation` - Type d'opération à effectuer (défaut: TaskOperation.DEFAULT)

##### getTask()

Récupère les détails d'une tâche par son ID.

```typescript
async getTask(taskId: string): Promise<TaskModel>
```

##### getUserTasks()

Récupère les tâches de l'utilisateur authentifié.

```typescript
async getUserTasks(page?: number, pageSize?: number): Promise<TaskModel[]>
```

Paramètres:
- `page` - Numéro de page (défaut: 1)
- `pageSize` - Nombre de tâches par page (défaut: 10)

##### waitForTask()

Attend qu'une tâche se termine.

```typescript
async waitForTask(
  taskId: string,
  pollInterval?: number,
  maxWaitTime?: number
): Promise<TaskModel>
```

Paramètres:
- `taskId` - ID de la tâche
- `pollInterval` - Intervalle entre les vérifications en ms (défaut: 2000)
- `maxWaitTime` - Temps d'attente maximum en ms (défaut: 300000)

##### getTaskText()

Récupère le texte extrait d'une tâche terminée.

```typescript
async getTaskText(taskId: string): Promise<string>
```

##### processDocument()

Traite un document de bout en bout (upload + attente + récupération).

```typescript
async processDocument(
  filePath: string,
  groupId?: string,
  taskOperation?: TaskOperation,
  pollInterval?: number,
  maxWaitTime?: number
): Promise<ProcessResponse[]>
```

## Structure du Package

```
sdk-js/
├── src/
│   ├── index.ts           # Exports publics
│   ├── client.ts          # Client synchrone
│   ├── models.ts          # Types et interfaces TypeScript
│   └── exceptions.ts      # Exceptions personnalisées
├── examples/
│   ├── sync-example.ts    # Exemple d'utilisation complète
│   └── process-document.ts # Exemple de traitement simplifié
├── dist/                  # Fichiers compilés (généré par build)
├── package.json           # Configuration du package
├── tsconfig.json          # Configuration TypeScript
└── README.md              # Documentation
```

## Compatibilité

- Node.js >= 18.0.0
- TypeScript >= 5.3.0 (pour le développement)
- axios >= 1.6.5
- form-data >= 4.0.0

## Développement

### Installation en mode développement

```bash
cd sdk-js
npm install
```

### Build

```bash
npm run build
```

### Tests

Les tests peuvent être ajoutés dans le futur:

```bash
npm test
```

## Comparaison avec le SDK Python

Le SDK JavaScript offre les mêmes fonctionnalités que le SDK Python:

| Fonctionnalité | Python SDK | JavaScript SDK |
|----------------|------------|----------------|
| Client synchrone | ✅ | ✅ |
| Client asynchrone | ✅ | ✅ (natif via async/await) |
| Types stricts | ✅ (Pydantic) | ✅ (TypeScript) |
| Context managers | ✅ | ⚠️ (pas nécessaire en JS) |
| Gestion des erreurs | ✅ | ✅ |
| Authentification | ✅ | ✅ |
| Méthodes utilitaires | ✅ | ✅ |

## Licence

Voir le fichier LICENSE du projet parent.

## Support

Pour signaler des bugs ou demander des fonctionnalités, veuillez ouvrir une issue sur le dépôt GitHub du projet.
