<template>
  <div class="flex flex-col gap-8">

    <!-- Guide d'utilisation -->
    <div class="rounded-lg border border-blue-200 bg-blue-50 px-5 py-4 text-sm text-blue-900">
      <p class="font-semibold mb-2 flex items-center gap-2">
        <span class="fr-icon-information-line" aria-hidden="true" />
        Extraction d'entités
      </p>
      <p class="text-blue-800 mb-1">
        Extrayez automatiquement des informations structurées (noms, dates, montants…) depuis vos documents scannés.
      </p>
      <ol class="list-decimal ml-5 flex flex-col gap-0.5 text-blue-800 text-xs">
        <li>Définissez les entités à rechercher (nom, type, description).</li>
        <li>Téléversez un document (PDF, JPG, PNG).</li>
        <li>Lancez l'extraction — le modèle analyse le texte et identifie chaque entité.</li>
      </ol>
    </div>

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

        <div v-if="isPolling" class="flex flex-col gap-2">
          <ProgressBar
            :visible="true"
            :progress="ocrProgress"
            text="OCR"
          />
          <ProgressBar
            :visible="chunkStarted"
            :progress="chunkProgress"
            text="Découpage"
          />
          <ProgressBar
            :visible="extractionStarted"
            :progress="extractionProgress"
            text="Extraction d'entités"
          />
        </div>
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
import { useRouter } from 'vue-router'
import ProgressBar from '@/components/ProgressBar.vue'
import EntityDefinitionModal from '@/components/EntityDefinitionModal.vue'
import type { EntityDefinition } from '@/components/EntityDefinitionModal.vue'
import createHttpClient from '@/api/http-client'
import { OCR_API_URL } from '@/utils/constants'
import useToaster from '@/composables/use-toaster'

type EntityType = EntityDefinition['entity_type']

const http = createHttpClient(OCR_API_URL)
const { addErrorMessage, addSuccessMessage } = useToaster()
const router = useRouter()

const files = ref<File | null>(null)
const uploadError = ref<string | undefined>(undefined)
const uploadAccept = '.pdf,.jpg,.png'
const isPolling = ref(false)
const status = ref<string | null>(null)
const ocrProgress = ref(0)
const chunkProgress = ref(0)
const extractionProgress = ref(0)
const chunkStarted = ref(false)
const extractionStarted = ref(false)

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
}

async function pollTask(taskId: string) {
  try {
    const [{ data: task }, { data: ocrChildren }] = await Promise.all([
      http.get<any>(`/tasks/${taskId}`),
      http.get<any[]>(`/tasks/${taskId}/children`),
    ])
    status.value = task.status

    // OCR progress from parent task
    ocrProgress.value = (task.status === 'in_progress' || task.status === 'started')
      ? Math.round((task.percentage ?? 0) * 100)
      : 100

    if (task.status === 'failed') {
      isPolling.value = false
      uploadError.value = task.extras?.error ?? 'Échec du traitement OCR.'
      addErrorMessage({ title: 'Échec :', description: uploadError.value ?? '' })
      return
    }

    // Chunk child (direct child of OCR task)
    const chunkChild = (ocrChildren as any[]).find((c: any) => c.type === 'tasks.ocr_chunk')

    if (chunkChild) {
      chunkStarted.value = true
      chunkProgress.value = chunkChild.status === 'completed'
        ? 100
        : Math.round((chunkChild.percentage ?? 0) * 100)

      if (chunkChild.status === 'failed') {
        isPolling.value = false
        uploadError.value = chunkChild.extras?.error ?? 'Échec du découpage.'
        addErrorMessage({ title: 'Échec :', description: uploadError.value ?? '' })
        return
      }

      // Entity extraction child (child of chunk task)
      const { data: chunkChildren } = await http.get<any[]>(`/tasks/${chunkChild.id}/children`)
      const entityChild = (chunkChildren as any[]).find((c: any) => c.type === 'tasks.entity_extraction')

      if (entityChild) {
        extractionStarted.value = true

        if (entityChild.status === 'completed') {
          extractionProgress.value = 100
          isPolling.value = false
          addSuccessMessage({ title: 'Extraction terminée', description: 'Redirection vers les résultats...' })
          router.push(`/${entityChild.id}`)
          return
        }
        else if (entityChild.status === 'failed') {
          isPolling.value = false
          uploadError.value = entityChild.extras?.error ?? "Échec de l'extraction."
          addErrorMessage({ title: 'Échec :', description: uploadError.value ?? '' })
          return
        }
        else {
          extractionProgress.value = Math.round((entityChild.percentage ?? 0) * 100)
        }
      }
    }

    pollingTimer = setTimeout(() => pollTask(taskId), 2000)
  }
  catch (err: any) {
    isPolling.value = false
    uploadError.value = err.message ?? 'Erreur lors du polling.'
  }
}

async function startExtraction() {
  if (!files.value) return

  uploadError.value = undefined
  ocrProgress.value = 0
  chunkProgress.value = 0
  extractionProgress.value = 0
  chunkStarted.value = false
  extractionStarted.value = false
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
