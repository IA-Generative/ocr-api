<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import TemplateFieldsModal from '@/components/TemplateFieldsModal.vue'
import TemplateApplyModal from '@/components/TemplateApplyModal.vue'
import type { EntityDefinition } from '@/components/EntityDefinitionModal.vue'
import type { TemplatingModel } from '@/stores/templating'
import { useTemplatingStore } from '@/stores/templating'

const props = withDefaults(defineProps<{ fullscreen?: boolean }>(), { fullscreen: false })
const router = useRouter()

const store = useTemplatingStore()
const { templatings: templates, isLoading, error: fetchError, taskInfos } = storeToRefs(store)

const isDragging = ref(false)
const selectedFile = ref<File | null>(null)
const uploadError = ref<string | null>(null)
const isUploading = ref(false)
const uploadSuccess = ref(false)
const newTemplateName = ref('')
const newTemplateDescription = ref('')

onMounted(() => {
  store.fetchTemplatings()
  // poll task statuses every 5s until all are completed
  pollInterval = window.setInterval(async () => {
    const pending = templates.value.filter((t: TemplatingModel) => {
      const info = taskInfos.value[t.id]
      return !info || !['completed', 'failed', 'canceled', 'revoked'].includes(info.status)
    })
    if (pending.length === 0) {
      clearInterval(pollInterval!)
      return
    }
    await Promise.all(pending.map((t: TemplatingModel) => store.fetchTaskInfo(t.id)))
  }, 5000)
})

let pollInterval: number | null = null
onUnmounted(() => { if (pollInterval) clearInterval(pollInterval) })

function isTaskDone (id: string): boolean {
  return taskInfos.value[id]?.status === 'completed'
}

function getTaskProgress (id: string): number {
  const info = taskInfos.value[id]
  if (!info) return 0
  if (info.status === 'completed') return 100
  return info.percentage ?? 0
}

function getTaskStatusLabel (id: string): string {
  const status = taskInfos.value[id]?.status
  const labels: Record<string, string> = {
    created: 'Créé',
    queued: 'En attente',
    started: 'Démarré',
    in_progress: 'En cours',
    completed: 'Terminé',
    failed: 'Échoué',
    canceled: 'Annulé',
    retrying: 'Nouvelle tentative',
    timeout: 'Timeout',
    revoked: 'Révoqué',
  }
  return status ? (labels[status] ?? status) : 'En attente'
}

const ACCEPTED_TYPES = ['application/vnd.oasis.opendocument.text']

function onDragOver (e: DragEvent) {
  e.preventDefault()
  isDragging.value = true
}

function onDragLeave () {
  isDragging.value = false
}

function onDrop (e: DragEvent) {
  e.preventDefault()
  isDragging.value = false
  const file = e.dataTransfer?.files[0]
  if (file) validateAndSetFile(file)
}

function onFileInput (e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) validateAndSetFile(file)
}

function validateAndSetFile (file: File) {
  uploadError.value = null
  uploadSuccess.value = false
  if (!ACCEPTED_TYPES.includes(file.type)) {
    uploadError.value = 'Format non supporté. Seuls les fichiers .odt sont acceptés.'
    return
  }
  selectedFile.value = file
  // Pre-fill name from filename if empty
  if (!newTemplateName.value) {
    newTemplateName.value = file.name.replace(/\.[^/.]+$/, '')
  }
}

async function uploadTemplate () {
  if (!selectedFile.value) return
  if (!newTemplateName.value.trim()) {
    uploadError.value = 'Veuillez renseigner un nom pour le template.'
    return
  }
  isUploading.value = true
  uploadError.value = null
  try {
    await store.uploadTemplating(
      selectedFile.value,
      newTemplateName.value.trim(),
      newTemplateDescription.value.trim(),
    )
    uploadSuccess.value = true
    selectedFile.value = null
    newTemplateName.value = ''
    newTemplateDescription.value = ''
  }
  catch (e: unknown) {
    uploadError.value = (e as Error).message ?? 'Erreur lors de l\'import.'
  }
  finally {
    isUploading.value = false
  }
}

async function deleteTemplate (id: string) {
  await store.deleteTemplating(id)
}

const configuringTemplate = ref<typeof templates.value[0] | null>(null)
const applyingTemplate = ref<typeof templates.value[0] | null>(null)
const templateFields = ref<Record<string, EntityDefinition[]>>({})

function allFieldsDefined (template: TemplatingModel): boolean {
  const zones = template.entity_zone ?? []
  return zones.length > 0 && zones.every(ez => !!ez.entity_definition?.definition)
}

function onFieldsSaved (fields: EntityDefinition[]) {
  if (configuringTemplate.value) {
    templateFields.value[configuringTemplate.value.id] = fields
  }
  configuringTemplate.value = null
  // refresh list to get updated entity_zone
  store.fetchTemplatings()
}
</script>

<template>
  <div :class="props.fullscreen ? 'fr-container fr-py-6w' : ''">
    <div class="flex items-center justify-between fr-mb-2w">
      <div class="flex items-center gap-2">
        <button
          v-if="props.fullscreen"
          class="fr-btn fr-btn--tertiary fr-btn--sm"
          title="Retour"
          @click="router.push('/')"
        >
          <span class="fr-icon-arrow-left-line" aria-hidden="true" />
        </button>
        <h2 class="fr-h4 fr-mb-0">Templates</h2>
      </div>
      <button
        v-if="!props.fullscreen"
        class="fr-btn fr-btn--tertiary fr-btn--sm"
        title="Ouvrir en plein écran"
        @click="router.push('/templates')"
      >
        <span class="fr-icon-fullscreen-line" aria-hidden="true" />
      </button>
    </div>
    <p class="fr-text--md fr-mb-4w">
      Importez des documents de référence pour configurer vos modèles de reconnaissance.
    </p>

    <!-- Upload zone -->
    <div class="fr-card fr-card--no-arrow fr-mb-6w">
      <div class="fr-card__body">
        <div class="fr-card__content">
          <h2 class="fr-h5 fr-mb-2w">Importer un template</h2>

          <div
            class="upload-zone"
            :class="{ 'upload-zone--active': isDragging }"
            @dragover="onDragOver"
            @dragleave="onDragLeave"
            @drop="onDrop"
          >
            <span class="fr-icon-upload-2-line fr-icon--lg" aria-hidden="true" />
            <p class="fr-mt-2w fr-mb-1w fr-text--md">
              Glissez-déposez un fichier ici ou
            </p>
            <label class="fr-btn fr-btn--secondary fr-btn--sm" for="file-input">
              Parcourir
            </label>
            <input
              id="file-input"
              type="file"
              accept=".odt"
              class="fr-sr-only"
              @change="onFileInput"
            />
            <p class="fr-text--sm fr-text--mention-grey fr-mt-2w fr-mb-0">
              Format accepté : ODT (OpenDocument Text)
            </p>
          </div>

          <!-- Selected file -->
          <div v-if="selectedFile" class="fr-mt-3w fr-mb-2w selected-file">
            <span class="fr-icon-file-line" aria-hidden="true" />
            <span class="fr-ml-1w">{{ selectedFile.name }}</span>
            <span class="fr-text--sm fr-text--mention-grey fr-ml-1w">
              ({{ (selectedFile.size / 1024).toFixed(1) }} Ko)
            </span>
            <button class="fr-btn fr-btn--tertiary-no-outline fr-btn--sm fr-ml-2w" @click="selectedFile = null; newTemplateName = ''; newTemplateDescription = ''">
              <span class="fr-icon-close-line" aria-hidden="true" />
            </button>
          </div>

          <!-- Name & description -->
          <div v-if="selectedFile" class="fr-mt-3w fr-grid-row fr-grid-row--gutters">
            <div class="fr-col-12 fr-col-md-6">
              <div class="fr-input-group">
                <label class="fr-label" for="template-name">
                  Nom du template <span class="fr-text--mention-grey">(requis)</span>
                </label>
                <input
                  id="template-name"
                  v-model="newTemplateName"
                  class="fr-input"
                  type="text"
                  placeholder="ex: Facture fournisseur"
                />
              </div>
            </div>
            <div class="fr-col-12 fr-col-md-6">
              <div class="fr-input-group">
                <label class="fr-label" for="template-description">Description</label>
                <input
                  id="template-description"
                  v-model="newTemplateDescription"
                  class="fr-input"
                  type="text"
                  placeholder="ex: Factures A4 fournisseurs France"
                />
              </div>
            </div>
          </div>

          <!-- Error -->
          <div v-if="uploadError" class="fr-alert fr-alert--error fr-alert--sm fr-mt-2w">
            <p>{{ uploadError }}</p>
          </div>

          <!-- Success -->
          <div v-if="uploadSuccess" class="fr-alert fr-alert--success fr-alert--sm fr-mt-2w">
            <p>Template importé avec succès.</p>
          </div>

          <button
            class="fr-btn fr-mt-3w"
            :disabled="!selectedFile || isUploading"
            @click="uploadTemplate"
          >
            <span v-if="isUploading">
              <span class="fr-icon-loader-line fr-mr-1w" aria-hidden="true" />
              Import en cours…
            </span>
            <span v-else>Importer</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Templates list -->
    <h2 class="fr-h5 fr-mb-3w">Templates disponibles ({{ templates.length }})</h2>

    <div v-if="isLoading" class="fr-text--mention-grey fr-mb-4w">
      <span class="fr-icon-loader-line fr-mr-1w" aria-hidden="true" />
      Chargement…
    </div>

    <div v-else-if="fetchError" class="fr-alert fr-alert--error fr-alert--sm fr-mb-4w">
      <p>{{ fetchError }}</p>
    </div>

    <div v-else-if="templates.length === 0" class="fr-text--mention-grey fr-mb-4w">
      Aucun template disponible. Importez votre premier document.
    </div>

    <div class="fr-grid-row fr-grid-row--gutters">
      <div
        v-for="template in templates"
        :key="template.id"
        class="fr-col-12 fr-col-md-6 fr-col-lg-4"
      >
        <div class="fr-card fr-card--no-arrow">
          <div class="fr-card__body">
            <div class="fr-card__content">
              <div class="template-header">
                <span class="fr-badge fr-badge--blue-cumulus">ODT</span>
                <button
                  class="fr-btn fr-btn--tertiary-no-outline fr-btn--sm fr-ml-auto"
                  title="Supprimer"
                  @click="deleteTemplate(template.id)"
                >
                  <span class="fr-icon-delete-line" aria-hidden="true" />
                </button>
              </div>
              <h3 class="fr-card__title fr-mt-2w fr-mb-1w">{{ template.name }}</h3>
              <p class="fr-card__desc fr-text--sm">{{ template.description }}</p>
              <p class="fr-text--xs fr-text--mention-grey fr-mb-2w">
                <span>Importé le {{ new Date(template.created_at * 1000).toLocaleDateString('fr-FR') }}</span>
                <span v-if="template.updated_at !== template.created_at" class="fr-ml-2w">
                  · Mis à jour le {{ new Date(template.updated_at * 1000).toLocaleDateString('fr-FR') }}
                </span>
              </p>

              <!-- Task progress -->
              <div class="fr-mb-2w">
                <div class="task-progress-header">
                  <span class="fr-text--xs fr-text--mention-grey">Analyse ODT : {{ getTaskStatusLabel(template.id) }}</span>
                  <span class="fr-text--xs fr-text--mention-grey">{{ getTaskProgress(template.id) }}%</span>
                </div>
                <div class="task-progress-bar">
                  <div
                    class="task-progress-fill"
                    :class="{
                      'task-progress-fill--done': isTaskDone(template.id),
                      'task-progress-fill--failed': taskInfos[template.id]?.status === 'failed',
                    }"
                    :style="{ width: getTaskProgress(template.id) + '%' }"
                  />
                </div>
              </div>

              <div class="flex gap-2 flex-wrap">
                <button
                  class="fr-btn fr-btn--secondary fr-btn--sm"
                  :disabled="!isTaskDone(template.id)"
                  @click="configuringTemplate = template"
                >
                  <span class="fr-icon-settings-5-line fr-mr-1w" aria-hidden="true" />
                  <span>Configurer les champs</span>
                </button>
                <button
                  v-if="allFieldsDefined(template)"
                  class="fr-btn fr-btn--sm"
                  @click="applyingTemplate = template"
                >
                  <span class="fr-icon-play-line fr-mr-1w" aria-hidden="true" />
                  <span>Lancer l'extraction</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <TemplateFieldsModal
    v-if="configuringTemplate"
    :template="configuringTemplate"
    @close="configuringTemplate = null"
    @save="onFieldsSaved"
  />

  <TemplateApplyModal
    v-if="applyingTemplate"
    :template="applyingTemplate"
    @close="applyingTemplate = null"
  />
</template>

<style scoped>
.upload-zone {
  border: 2px dashed var(--border-default-grey);
  border-radius: 4px;
  padding: 2.5rem;
  text-align: center;
  transition: background-color 0.2s, border-color 0.2s;
  cursor: default;
}

.upload-zone--active {
  border-color: var(--border-action-high-blue-france);
  background-color: var(--background-action-low-blue-france);
}

.selected-file {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  background: var(--background-alt-grey);
  border-radius: 4px;
}

.template-header {
  display: flex;
  align-items: center;
}

.task-progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.task-progress-bar {
  height: 6px;
  background: var(--background-alt-grey);
  border-radius: 3px;
  overflow: hidden;
}

.task-progress-fill {
  height: 100%;
  background: var(--border-action-high-blue-france);
  border-radius: 3px;
  transition: width 0.4s ease;
}

.task-progress-fill--done {
  background: var(--text-default-success);
}

.task-progress-fill--failed {
  background: var(--text-default-error);
}
</style>
