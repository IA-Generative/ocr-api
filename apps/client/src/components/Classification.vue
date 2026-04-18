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
            :disabled="!files || documentTypes.length === 0 || isPolling"
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
        <div class="flex items-center justify-between">
          <div>
            <h3 class="fr-h5 mb-1">Types de documents attendus</h3>
            <p class="fr-text--sm text-[var(--text-mention-grey)]">
              Définissez chaque type de document que le modèle doit reconnaître.
            </p>
          </div>
          <button
            class="fr-btn fr-btn--tertiary fr-btn--sm fr-icon-add-line shrink-0"
            type="button"
            @click="openCreate"
          >
            Ajouter
          </button>
        </div>

        <!-- Liste vide -->
        <div
          v-if="documentTypes.length === 0"
          class="flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed border-slate-200 py-10 text-slate-400"
        >
          <span class="fr-icon-file-text-line" style="font-size: 28px;" aria-hidden="true" />
          <p class="text-sm">Aucun type de document défini</p>
          <button
            class="fr-btn fr-btn--tertiary fr-btn--sm fr-icon-add-line"
            type="button"
            @click="openCreate"
          >
            Ajouter un type
          </button>
        </div>

        <!-- Cards -->
        <div class="flex flex-col gap-2">
          <div
            v-for="(docType, index) in documentTypes"
            :key="index"
            class="flex items-start gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm hover:border-slate-300 transition-colors"
          >
            <span class="mt-0.5 shrink-0 px-2 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-700">
              Type
            </span>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-slate-800 truncate">{{ docType.name }}</p>
              <p class="text-xs text-slate-500 mt-0.5 line-clamp-2">{{ docType.description }}</p>
            </div>
            <div class="flex gap-1 shrink-0">
              <button
                class="fr-btn fr-btn--tertiary-no-outline fr-btn--sm fr-icon-edit-line text-slate-400 hover:text-slate-700"
                type="button"
                :aria-label="`Modifier ${docType.name}`"
                @click="openEdit(index)"
              />
              <button
                class="fr-btn fr-btn--tertiary-no-outline fr-btn--sm fr-icon-delete-line text-slate-400 hover:text-red-500"
                type="button"
                :aria-label="`Supprimer ${docType.name}`"
                @click="documentTypes.splice(index, 1)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Résultat CLASSIFICATION -->
    <div v-if="taskOutput && !isPolling" class="flex flex-col gap-6">
      <ClassificationResult v-if="classificationPages.length > 0" :pages="classificationPages" />
      <OcrViewer :data="taskOutput" />
    </div>

    <!-- Modal ajout/édition -->
    <DocTypeModal
      v-if="modalOpen"
      :initial="editingIndex !== null ? documentTypes[editingIndex] : undefined"
      @close="closeModal"
      @save="onSave"
    />

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import ProgressBar from '@/components/ProgressBar.vue'
import OcrViewer from '@/components/OcrViewer.vue'
import ClassificationResult from '@/components/ClassificationResult.vue'
import type { ClassificationPage } from '@/components/ClassificationResult.vue'
import DocTypeModal from '@/components/DocTypeModal.vue'
import type { DocumentType } from '@/components/DocTypeModal.vue'
import createHttpClient from '@/api/http-client'
import { OCR_API_URL } from '@/utils/constants'
import useToaster from '@/composables/use-toaster'

const http = createHttpClient(OCR_API_URL)
const { addErrorMessage, addSuccessMessage } = useToaster()

const files = ref<File | null>(null)
const isPolling = ref(false)
const status = ref<string | null>(null)
const progressPercent = ref(0)
const taskOutput = ref<{ id: string; pages: any[] } | null>(null)
const uploadError = ref<string | undefined>(undefined)

let pollingTimer: ReturnType<typeof setTimeout> | null = null

const documentTypes = ref<DocumentType[]>([])

const modalOpen = ref(false)
const editingIndex = ref<number | null>(null)

function openCreate () {
  editingIndex.value = null
  modalOpen.value = true
}

function openEdit (index: number) {
  editingIndex.value = index
  modalOpen.value = true
}

function closeModal () {
  modalOpen.value = false
  editingIndex.value = null
}

function onSave (docType: DocumentType) {
  if (editingIndex.value !== null) {
    documentTypes.value[editingIndex.value] = docType
  }
  else {
    documentTypes.value.push(docType)
  }
  closeModal()
}

const getNormalizedDocumentTypes = () =>
  documentTypes.value.map((d: DocumentType) => ({
    label: d.name.toLowerCase().trim().replace(/[^a-z0-9_]/g, '_').replace(/_+/g, '_'),
    definition: d.description.trim(),
  }))

async function pollTask(taskId: string) {
  try {
    const { data: task } = await http.get<any>(`/tasks/${taskId}`)
    status.value = task.status

    if (task.status === 'in_progress' || task.status === 'started') {
      progressPercent.value = Math.round((task.percentage ?? 0) * 100)
      pollingTimer = setTimeout(() => pollTask(taskId), 2000)
    }
    else if (task.status === 'completed') {
      progressPercent.value = 100
      isPolling.value = false
      taskOutput.value = { id: taskId, pages: task.output?.pages ?? [] }
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
  taskOutput.value = null
}

async function startOcr() {
  if (!files.value) return

  uploadError.value = undefined
  taskOutput.value = null
  progressPercent.value = 0
  isPolling.value = true
  status.value = null

  const form = new FormData()
  form.append('file', files.value)
  form.append('task_operation', 'page_classification')
  form.append('task_name', 'tasks.page_text_classification')
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
  taskOutput.value = null
})

onBeforeUnmount(() => {
  if (pollingTimer) clearTimeout(pollingTimer)
})

const uploadLabel = 'Téléverser un document'
const uploadHint = 'Formats acceptés : PDF, JPG, PNG'
const uploadAccept = '.pdf,.jpg,.png'

const classificationPages = computed<ClassificationPage[]>(() => {
  if (!taskOutput.value) return []
  return taskOutput.value.pages
    .filter((p: any) => p.classifications && p.classifications.length > 0)
    .map((p: any) => {
      const classifications = p.classifications.map((c: any) => ({
        label: c.label,
        confidence: c.confidence,
        scorePercent: Math.round(c.confidence * 100),
      }))
      const topLabel = classifications.reduce(
        (best: any, c: any) => (c.confidence > (best?.confidence ?? -1) ? c : best),
        null as any,
      )?.label?.label ?? null
      return {
        page: p.page,
        pageUrl: p.page_url ?? null,
        topLabel,
        classifications,
      }
    })
})
</script>
