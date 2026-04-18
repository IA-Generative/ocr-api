<template>
  <div class="flex flex-col gap-8">

    <!-- SECTION PRINCIPALE : Upload + Entités -->
    <div class="flex flex-col gap-6 md:flex-row md:gap-10">

      <!-- COLONNE GAUCHE : Upload + bouton -->
      <div class="flex flex-col gap-4 flex-1">
        <DsfrFileUpload
          label="Téléverser un document"
          hint="Formats acceptés : PDF, JPG, PNG"
          :accept="uploadAccept"
          :error="uploadError"
          @change="selectFile"
        />

        <div>
          <DsfrButton
            label="Lancer l'extraction"
            size="lg"
            :disabled="!canSubmit"
            @click="startExtraction"
          />
        </div>

        <ProgressBar
          :visible="isPolling && status === 'in_progress'"
          :progress="progressPercent"
        />
      </div>

      <!-- COLONNE DROITE : Entités -->
      <div class="flex flex-col gap-4 flex-1">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="fr-h5 mb-1">Entités à extraire</h3>
            <p class="fr-text--sm text-[var(--text-mention-grey)]">
              Définissez chaque entité que le modèle doit rechercher dans le document.
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
          v-if="entities.length === 0"
          class="flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed border-slate-200 py-10 text-slate-400"
        >
          <span class="fr-icon-list-unordered" style="font-size: 28px;" aria-hidden="true" />
          <p class="text-sm">Aucune entité définie</p>
          <button
            class="fr-btn fr-btn--tertiary fr-btn--sm fr-icon-add-line"
            type="button"
            @click="openCreate"
          >
            Ajouter une entité
          </button>
        </div>

        <!-- Cards entités -->
        <div class="flex flex-col gap-2">
          <div
            v-for="(entity, index) in entities"
            :key="index"
            class="flex items-start gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm hover:border-slate-300 transition-colors"
          >
            <!-- Badge type -->
            <span
              class="mt-0.5 shrink-0 px-2 py-0.5 rounded-full text-xs font-semibold"
              :style="typeStyle(entity.entity_type)"
            >
              {{ labelFor(entity.entity_type) }}
            </span>

            <!-- Contenu -->
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-slate-800 truncate">{{ entity.name }}</p>
              <p class="text-xs text-slate-500 mt-0.5 line-clamp-2">{{ entity.definition }}</p>
              <div v-if="entity.formats?.length || entity.exemples?.length" class="flex flex-wrap gap-1 mt-2">
                <span
                  v-for="(fmt, fi) in entity.formats"
                  :key="`fmt-${fi}`"
                  class="inline-flex items-center gap-1 rounded-md bg-slate-100 px-1.5 py-0.5 text-xs text-slate-600"
                >
                  <span class="fr-icon-layout-line" style="font-size: 10px;" aria-hidden="true" />
                  {{ fmt }}
                </span>
                <span
                  v-for="(ex, ei) in entity.exemples"
                  :key="`ex-${ei}`"
                  class="inline-flex items-center gap-1 rounded-md bg-blue-50 px-1.5 py-0.5 text-xs text-blue-600"
                >
                  <span class="fr-icon-double-quote-line" style="font-size: 10px;" aria-hidden="true" />
                  {{ ex }}
                </span>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex gap-1 shrink-0">
              <button
                class="fr-btn fr-btn--tertiary-no-outline fr-btn--sm fr-icon-edit-line text-slate-400 hover:text-slate-700"
                type="button"
                :aria-label="`Modifier ${entity.name}`"
                @click="openEdit(index)"
              />
              <button
                class="fr-btn fr-btn--tertiary-no-outline fr-btn--sm fr-icon-delete-line text-slate-400 hover:text-red-500"
                type="button"
                :aria-label="`Supprimer ${entity.name}`"
                @click="entities.splice(index, 1)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Résultats extraction -->
    <div v-if="extractedEntities.length > 0 && !isPolling">
      <EntityResult :entities="extractedEntities" />
    </div>

    <!-- Visualisation bboxes sur le document -->
    <div v-if="hasBboxes && !isPolling" class="flex flex-col gap-3">
      <div class="flex items-center justify-between">
        <h3 class="fr-h6 mb-0">Localisation des entités</h3>
        <div v-if="totalPages > 1" class="flex items-center gap-2">
          <button
            class="fr-btn fr-btn--tertiary-no-outline fr-btn--sm fr-icon-arrow-left-s-line"
            type="button"
            :disabled="currentPage === 0"
            aria-label="Page précédente"
            @click="currentPage = Math.max(0, currentPage - 1)"
          />
          <span class="text-sm text-slate-600">{{ currentPage + 1 }} / {{ totalPages }}</span>
          <button
            class="fr-btn fr-btn--tertiary-no-outline fr-btn--sm fr-icon-arrow-right-s-line"
            type="button"
            :disabled="currentPage >= totalPages - 1"
            aria-label="Page suivante"
            @click="currentPage = Math.min(totalPages - 1, currentPage + 1)"
          />
        </div>
      </div>
      <div class="relative rounded-xl overflow-hidden border border-slate-200 shadow-sm bg-slate-50">
        <OcrImageViewer
          :all-boxes="[]"
          :box-meta="[]"
          :show-image="true"
          :drawing-mode="false"
          :selected-box-idx="null"
          :image-url="currentPageImageUrl"
          view-mode="entity"
          :entity-boxes="currentPageEntities"
        />
      </div>
    </div>

    <!-- Modal ajout/édition -->
    <EntityDefinitionModal
      v-if="modalOpen"
      :initial="editingIndex !== null ? entities[editingIndex] : undefined"
      @close="closeModal"
      @save="onSave"
    />

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onBeforeUnmount } from 'vue'
import ProgressBar from '@/components/ProgressBar.vue'
import EntityDefinitionModal from '@/components/EntityDefinitionModal.vue'
import EntityResult from '@/components/EntityResult.vue'
import OcrImageViewer from '@/components/OcrImageViewer.vue'
import type { EntityDefinition } from '@/components/EntityDefinitionModal.vue'
import type { EntityPrediction } from '@/components/EntityResult.vue'
import createHttpClient from '@/api/http-client'
import { OCR_API_URL } from '@/utils/constants'
import useToaster from '@/composables/use-toaster'

type EntityType = EntityDefinition['entity_type']

const http = createHttpClient(OCR_API_URL)
const { addErrorMessage, addSuccessMessage } = useToaster()

const files = ref<File | null>(null)
const uploadError = ref<string | undefined>(undefined)
const uploadAccept = '.pdf,.jpg,.png'
const isPolling = ref(false)
const status = ref<string | null>(null)
const progressPercent = ref(0)
const extractedEntities = ref<EntityPrediction[]>([])
const taskPages = ref<any[]>([])
const currentPage = ref(0)

const currentPageImageUrl = computed<string | undefined>(() => {
  return taskPages.value[currentPage.value]?.page_url ?? undefined
})

// Pages are 0-indexed in entity data; show entities that match or have no page info
const currentPageEntities = computed<EntityPrediction[]>(() => {
  return extractedEntities.value.filter((e: EntityPrediction) =>
    !e.pages || e.pages.length === 0 || e.pages.includes(currentPage.value),
  )
})

// Total pages: prefer server pages array, fallback to max page index from entities
const totalPages = computed(() => {
  if (taskPages.value.length > 0) return taskPages.value.length
  const maxPage = extractedEntities.value.reduce((max: number, e: EntityPrediction) => {
    const m = e.pages ? Math.max(...e.pages) : 0
    return Math.max(max, m)
  }, 0)
  return maxPage + 1
})

const hasBboxes = computed(() => {
  return extractedEntities.value.some((e: EntityPrediction) => e.bbox && e.bbox.length > 0)
})

let pollingTimer: ReturnType<typeof setTimeout> | null = null

const entities = ref<EntityDefinition[]>([])

const modalOpen = ref(false)
const editingIndex = ref<number | null>(null)

const canSubmit = computed(() => !!files.value && entities.value.length > 0 && !isPolling.value)

// Mapping frontend types → backend EntityType enum
const TYPE_MAP: Record<EntityType, string> = {
  string: 'text',
  int: 'integer',
  float: 'float',
  date: 'date',
  boolean: 'boolean',
  email: 'email',
  phone: 'phone_number',
  address: 'text',
  currency: 'text',
  iban: 'text',
}

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

function onSave (entity: EntityDefinition) {
  if (editingIndex.value !== null) {
    entities.value[editingIndex.value] = entity
  }
  else {
    entities.value.push(entity)
  }
  closeModal()
}

const selectFile = (selected: FileList | File[]) => {
  files.value = Array.isArray(selected) ? selected[0] ?? null : selected[0] ?? null
  uploadError.value = undefined
  extractedEntities.value = []
}

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
      taskPages.value = task.output?.pages ?? []
      extractedEntities.value = task.output?.entities ?? []
      addSuccessMessage({ title: 'Extraction terminée', description: 'Les entités sont disponibles.' })
    }
    else if (task.status === 'failed') {
      isPolling.value = false
      uploadError.value = task.extras?.error ?? "Échec de l'extraction."
      addErrorMessage({ title: 'Échec :', description: uploadError.value ?? '' })
    }
    else {
      pollingTimer = setTimeout(() => pollTask(taskId), 2000)
    }
  }
  catch (err: any) {
    isPolling.value = false
    uploadError.value = err.message ?? 'Erreur lors du polling.'
  }
}

async function startExtraction() {
  if (!files.value) return

  uploadError.value = undefined
  extractedEntities.value = []
  taskPages.value = []
  currentPage.value = 0
  progressPercent.value = 0
  isPolling.value = true
  status.value = null

  const parameter = {
    name: 'extraction',
    definition: 'Entity extraction',
    entity_type: 'text',
    formats: [],
    exemples: [],
    entities_definitions: entities.value.map(e => ({
      name: e.name,
      definition: e.definition,
      entity_type: TYPE_MAP[e.entity_type] ?? 'text',
      formats: e.formats ?? [],
      exemples: e.exemples ?? [],
    })),
  }

  const form = new FormData()
  form.append('file', files.value)
  form.append('task_operation', 'entity_extraction')
  form.append('task_name', 'tasks.entity_extraction')
  form.append('parameter', JSON.stringify(parameter))

  try {
    const { data: task } = await http.post<any>('/jobs/', form)
    if (!task?.id) throw new Error('ID de tâche manquant')
    await pollTask(task.id)
  }
  catch (err: any) {
    isPolling.value = false
    uploadError.value = err.message ?? "Erreur lors de l'envoi."
    addErrorMessage({ title: 'Erreur :', description: uploadError.value ?? '' })
  }
}

onBeforeUnmount(() => {
  if (pollingTimer) clearTimeout(pollingTimer)
})

const TYPE_COLORS: Record<string, { bg: string; text: string }> = {
  string:   { bg: '#f1f5f9', text: '#475569' },
  int:      { bg: '#eff6ff', text: '#1d4ed8' },
  float:    { bg: '#eef2ff', text: '#4338ca' },
  date:     { bg: '#fdf4ff', text: '#7e22ce' },
  boolean:  { bg: '#f0fdf4', text: '#15803d' },
  email:    { bg: '#fff7ed', text: '#c2410c' },
  phone:    { bg: '#fff1f2', text: '#be123c' },
  address:  { bg: '#f0fdfa', text: '#0f766e' },
  currency: { bg: '#fefce8', text: '#a16207' },
  iban:     { bg: '#f0f9ff', text: '#0369a1' },
}

const TYPE_LABELS: Record<string, string> = {
  string: 'Texte', int: 'Entier', float: 'Décimal', date: 'Date',
  boolean: 'Oui/Non', email: 'Email', phone: 'Tél.', address: 'Adresse',
  currency: 'Montant', iban: 'IBAN',
}

function typeStyle (type: EntityType) {
  const c = TYPE_COLORS[type] ?? { bg: '#f1f5f9', text: '#475569' }
  return { backgroundColor: c.bg, color: c.text }
}

function labelFor (type: EntityType) {
  return TYPE_LABELS[type] ?? type
}
</script>
