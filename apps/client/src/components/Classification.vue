<template>
  <div class="fr-grid-row fr-grid-row--gutters">

    <!-- COLONNE GAUCHE -->
    <div class="fr-col-12 fr-col-md-6">

      <DsfrFileUpload
        v-model="files"
        :label="uploadLabel"
        :hint="uploadHint"
        :error="uploadError"
        :accept="uploadAccept"
      />

      <div class="fr-mt-3w">
        <DsfrButton
          label="Lancer l’analyse du document"
          size="lg"
          :disabled="isDisabled"
          @click="startOcr"
        />
      </div>

    </div>

    <!-- COLONNE DROITE -->
    <div class="fr-col-12 fr-col-md-6">

      <h3 class="fr-h5">Types de documents attendus</h3>

      <p class="fr-text--sm fr-mb-3w">
        Indiquez les types de documents que le modèle doit reconnaître (ex: CNI, facture, passeport).
      </p>

      <div
        v-for="(docType, index) in documentTypes"
        :key="index"
        class="fr-card fr-mb-3w fr-p-3w"
      >

        <!-- NAME -->
        <div class="fr-mb-2w">
          <label class="fr-label">
            Nom du type de document
          </label>

          <input
            v-model="docType.name"
            class="fr-input"
            type="text"
            placeholder="ex: cni"
          />

          <p v-if="typeError(docType)" class="fr-error-text">
            Format invalide : uniquement minuscules, chiffres et underscore
          </p>
        </div>

        <!-- DESCRIPTION -->
        <div class="fr-mb-2w">

          <div class="fr-flex fr-align-items-center fr-gap-1v">
            <label class="fr-label">
              Description (anglais fortement recommandé)
            </label>

            <button
              class="fr-btn fr-btn--tertiary-no-outline fr-icon-information-line"
              type="button"
              :title="tooltipText"
              aria-label="Information sur la description"
            />
          </div>

          <textarea
            v-model="docType.description"
            class="fr-input"
            rows="3"
            placeholder="Describe the document type in English"
          />

          <p class="fr-hint-text">
            Exemple : "French national identity card containing personal information and MRZ zone"
          </p>

        </div>


        <!-- DELETE -->
        <div class="fr-mt-2w">
          <DsfrButton
            label="Supprimer"
            secondary
            icon="fr-icon-delete-line"
            @click="removeDocumentType(index)"
          />
        </div>

      </div>

      <DsfrButton
        label="Ajouter un type de document"
        secondary
        icon="fr-icon-add-line"
        @click="addDocumentType"
      />

    </div>

    <!-- RESULT -->
    <div class="fr-col-12 fr-mt-5w flex justify-center">
      <OcrViewer
        v-if="taskData?.output && !isPolling"
        :data="{ id: taskData.id, pages: taskData.output.pages }"
      />
    </div>

    <!-- DEBUG -->
    <div class="fr-col-12">
      <pre>
files: {{ files }}
documentTypes: {{ documentTypes }}
      </pre>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";

/**
 * TYPES
 */
type DocumentType = {
  name: string;
  description: string;
};

/**
 * FILES
 */
const files = ref<File[]>([]);
const selectedFile = computed(() => files.value[0] || null);

/**
 * DOCUMENT TYPES (nouveau modèle)
 */
const documentTypes = ref<DocumentType[]>([
  { name: "cni", description: "" }
]);

/**
 * TOOLTIP
 */
const tooltipText =
  "Descriptions should preferably be written in English to improve OCR and LLM extraction quality.";

/**
 * VALIDATION NAME
 */
const isValidTypeName = (name: string) =>
  /^[a-z0-9_]+$/.test(name);

const typeError = (docType: DocumentType) =>
  docType.name && !isValidTypeName(docType.name);

/**
 * NORMALISATION (au submit uniquement)
 */
const getNormalizedDocumentTypes = () => {
  return documentTypes.value.map(d => ({
    ...d,
    name: d.name
      .toLowerCase()
      .trim()
      .replace(/[^a-z0-9_]/g, "_")
      .replace(/_+/g, "_"),
  }));
};

/**
 * ACTIONS
 */
const addDocumentType = () => {
  documentTypes.value.push({ name: "", description: "" });
};

const removeDocumentType = (index: number) => {
  documentTypes.value.splice(index, 1);
};

/**
 * DISABLE LOGIC
 */
const hasValidTypes = computed(() =>
  documentTypes.value.some(d => isValidTypeName(d.name))
);

const isDisabled = computed(() =>
  !selectedFile.value || !hasValidTypes.value
);

/**
 * OCR ACTION
 */
const startOcr = () => {
  console.log("file:", selectedFile.value);
  console.log("documentTypes:", getNormalizedDocumentTypes());
};

/**
 * MOCKS (à remplacer backend)
 */
const isPolling = ref(false);
const uploadLabel = "Téléverser un document";
const uploadHint = "Formats acceptés : PDF, JPG, PNG";
const uploadError = "";
const uploadAccept = ".pdf,.jpg,.png";
const taskData = ref<any>(null);
</script>