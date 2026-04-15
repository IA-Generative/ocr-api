<template>
  <div class="flex flex-col gap-8">

    <!-- SECTION PRINCIPALE : Upload + Types -->
    <div class="flex flex-col gap-6 md:flex-row md:gap-10">

      <!-- COLONNE GAUCHE : Upload + bouton -->
      <div class="flex flex-col gap-4 flex-1">
        <DsfrFileUpload
          :label="uploadLabel"
          :hint="uploadHint"
          :error="uploadError"
          :accept="uploadAccept"
          @change="selectFile"
        />

        <div>
          <DsfrButton
            label="Lancer la classification"
            size="lg"
            :disabled="isDisabled || isPolling"
            @click="startOcr"
          />
        </div>

        <ProgressBar
          :visible="isPolling && status === 'in_progress'"
          :progress="progressPercent"
        />
      </div>

      <!-- COLONNE DROITE : Types de documents -->
      <div class="flex flex-col gap-4 flex-1">
        <div>
          <h3 class="fr-h5 mb-1">Types de documents attendus</h3>
          <p class="fr-text--sm text-[var(--text-mention-grey)]">
            Définissez chaque type de document que le modèle doit être capable de reconnaître.
            Donnez un <strong>nom court</strong> (ex&nbsp;: <code>cni</code>, <code>facture</code>, <code>passeport</code>)
            et une <strong>description précise en anglais</strong> qui explique à quoi ressemble le document.
            Plus la description est détaillée, meilleure sera la classification.
          </p>
        </div>

        <!-- LABELS -->
        <div class="flex text-xs text-[var(--text-mention-grey)] gap-2 px-1">
          <span class="w-32 shrink-0">Nom</span>
          <span class="flex-1 flex items-center gap-1">
            Description <span class="text-[var(--text-default-error)] ml-0.5" title="Champ obligatoire">*</span>
            <InfoTooltip :text="tooltipText" />
          </span>
        </div>

        <div
          v-for="(docType, index) in documentTypes"
          :key="index"
          class="flex items-start gap-2"
        >
          <div class="w-32 shrink-0">
            <input
              v-model="docType.name"
              class="fr-input fr-input--sm"
              :class="{ 'fr-input--error': typeError(docType) }"
              type="text"
              placeholder="ex: cni"
              :title="typeError(docType) ? 'Uniquement minuscules, chiffres et underscore' : ''"
            />
          </div>

          <input
            v-model="docType.description"
            class="fr-input fr-input--sm flex-1"
            :class="{ 'fr-input--error': descriptionError(docType) }"
            type="text"
            placeholder="Ex: French national identity card with photo (required, in English)"
            :title="descriptionError(docType) ? 'La description est obligatoire et doit être en anglais' : 'Décrivez le document en anglais'"
          />

          <button
            class="fr-btn fr-btn--tertiary-no-outline fr-icon-delete-line fr-btn--sm mt-1 text-[var(--text-default-error)]"
            type="button"
            title="Supprimer"
            :aria-label="`Supprimer ${docType.name || 'ce type'}`"
            @click="removeDocumentType(index)"
          />
        </div>

        <div>
          <button
            class="fr-btn fr-btn--tertiary fr-btn--sm fr-icon-add-line"
            type="button"
            @click="addDocumentType"
          >
            Ajouter un type
          </button>
        </div>
      </div>
    </div>

    <!-- RÉSULTAT CLASSIFICATION -->
    <div v-if="classificationPages.length > 0 && !isPolling" class="border border-[var(--border-default-grey)] p-5">
      <ClassificationResult :pages="classificationPages" />
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import ProgressBar from '@/components/ProgressBar.vue'
import InfoTooltip from '@/components/InfoTooltip.vue'
import ClassificationResult from '@/components/ClassificationResult.vue'
import type { ClassificationPage } from '@/components/ClassificationResult.vue'
import createHttpClient from '@/api/http-client'
import { OCR_API_URL } from '@/utils/constants'
import useToaster from '@/composables/use-toaster'

const http = createHttpClient(OCR_API_URL)
const { addErrorMessage, addSuccessMessage } = useToaster()

type DocumentType = {
  name: string
  description: string
}

type ClassificationResultItem = {
  label: { label: string; definition: string }
  confidence: number
  scorePercent: number
}

const files = ref<File | null>(null)
const isPolling = ref(false)
const status = ref<string | null>(null)
const progressPercent = ref(0)
const classificationPages = ref<ClassificationPage[]>([])
const uploadError = ref<string | undefined>(undefined)

let pollingTimer: ReturnType<typeof setTimeout> | null = null

const documentTypes = ref<DocumentType[]>([
  { name: 'cni', description: '' },
])

const tooltipText =
  'La description est obligatoire. Rédigez-la en anglais pour de meilleurs résultats — le modèle LLM utilisé est optimisé pour cette langue.'

const isValidTypeName = (name: string) => /^[a-z0-9_]+$/.test(name)

const typeError = (docType: DocumentType) =>
  docType.name && !isValidTypeName(docType.name)

const descriptionError = (docType: DocumentType) =>
  docType.name && !docType.description.trim()

const getNormalizedDocumentTypes = () =>
  documentTypes.value
    .filter((d: DocumentType) => isValidTypeName(d.name))
    .map((d: DocumentType) => ({
      label: d.name.toLowerCase().trim().replace(/[^a-z0-9_]/g, '_').replace(/_+/g, '_'),
      definition: d.description.trim(),
    }))

const addDocumentType = () => { documentTypes.value.push({ name: '', description: '' }) }
const removeDocumentType = (index: number) => { documentTypes.value.splice(index, 1) }

const hasValidTypes = computed(() =>
  documentTypes.value.some((d: DocumentType) => isValidTypeName(d.name) && d.description.trim().length > 0),
)
const isDisabled = computed(() => !files.value || !hasValidTypes.value || isPolling.value)

function buildClassificationPages(pages: any[]): ClassificationPage[] {
  return pages
    .filter((p: any) => p.classifications?.length > 0)
    .map((p: any) => {
      const classifications: ClassificationResultItem[] = p.classifications.map((c: any) => ({
        label: c.label,
        confidence: c.confidence,
        // Cosine similarity CLIP : [-1, 1] → [0, 100]
        scorePercent: Math.round(Math.max(0, Math.min(100, ((c.confidence + 1) / 2) * 100)),
        ),
      }))
      classifications.sort((a, b) => b.scorePercent - a.scorePercent)
      return {
        page: p.page,
        pageUrl: p.page_url ?? null,
        topLabel: classifications[0]?.label?.label ?? null,
        classifications,
      }
    })
}

async function pollTask(taskId: string) {
  try {
    const { data: task } = await http.get<any>(`/tasks/${taskId}`)
    status.value = task.status

    if (task.status === 'in_progress') {
      progressPercent.value = Math.round((task.percentage ?? 0) * 100)
      pollingTimer = setTimeout(() => pollTask(taskId), 2000)
    }
    else if (task.status === 'completed') {
      progressPercent.value = 100
      isPolling.value = false
      const pages = task.output?.pages ?? []
      classificationPages.value = buildClassificationPages(pages)
      addSuccessMessage({ title: 'Classification terminée', description: 'Les résultats sont disponibles.' })
    }
    else if (task.status === 'failed') {
      isPolling.value = false
      uploadError.value = task.extras?.error ?? 'Échec de la classification.'
      addErrorMessage({ title: 'Échec :', description: uploadError.value ?? '' })
    }
    else {
      // queued / created / etc.
      pollingTimer = setTimeout(() => pollTask(taskId), 2000)
    }
  }
  catch (err: any) {
    isPolling.value = false
    uploadError.value = err.message ?? 'Erreur lors du polling.'
  }
}

const selectFile = (selected: FileList | File[]) => {
  files.value = Array.isArray(selected) ? selected[0] ?? null : selected[0] ?? null
  uploadError.value = undefined
  classificationPages.value = []
  status.value = null
  progressPercent.value = 0
}

async function startOcr() {
  if (!files.value) return

  uploadError.value = undefined
  classificationPages.value = []
  progressPercent.value = 0
  isPolling.value = true
  status.value = null

  const form = new FormData()
  form.append('file', files.value)
  form.append('task_operation', 'page_classification')
  form.append('task_name', 'tasks.page_classification')
  form.append('parameter', JSON.stringify({ labels: getNormalizedDocumentTypes() }))

  try {
    const { data: task } = await http.post<any>('/jobs/', form)
    if (!task?.id) throw new Error('ID de tâche manquant')
    await pollTask(task.id)
  }
  catch (err: any) {
    isPolling.value = false
    uploadError.value = err.message ?? 'Erreur lors de l\'envoi.'
    addErrorMessage({ title: 'Erreur :', description: uploadError.value ?? '' })
  }
}

onMounted(() => {
  classificationPages.value = []
})

onBeforeUnmount(() => {
  if (pollingTimer) clearTimeout(pollingTimer)
})

const uploadLabel = 'Téléverser un document'
const uploadHint = 'Formats acceptés : PDF, JPG, PNG'
const uploadAccept = '.pdf,.jpg,.png'
</script>
