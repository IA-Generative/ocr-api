<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center p-4"
    style="background: rgba(15,23,42,0.35); backdrop-filter: blur(3px);"
    @click.self="$emit('close')"
  >
    <div
      class="w-full max-w-2xl rounded-2xl bg-white shadow-2xl flex flex-col max-h-[90vh]"
      @click.stop
    >
      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100">
        <div>
          <h2 class="text-base font-semibold text-slate-800">Lancer l'extraction</h2>
          <p class="text-xs text-slate-400 mt-0.5">Template : {{ template.name }}</p>
        </div>
        <button
          class="text-slate-400 hover:text-slate-600 transition-colors"
          aria-label="Fermer"
          @click="$emit('close')"
        >
          <span class="fr-icon-close-line" aria-hidden="true" />
        </button>
      </div>

      <!-- Body -->
      <div class="flex-1 overflow-y-auto px-6 py-5">

        <!-- Before submission -->
        <template v-if="!isSubmitted">
          <p class="text-sm text-slate-500 mb-4">
            Sélectionnez les fichiers sur lesquels appliquer le template
            <span class="font-medium text-slate-700">{{ template.name }}</span>.
          </p>

          <!-- Drop zone -->
          <div
            class="border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer"
            :class="isDragging ? 'border-blue-france bg-blue-50' : 'border-slate-300 hover:border-slate-400'"
            @dragover.prevent="isDragging = true"
            @dragleave="isDragging = false"
            @drop.prevent="onDrop"
            @click="fileInputRef?.click()"
          >
            <span class="fr-icon-upload-2-line text-slate-400" style="font-size: 2rem;" aria-hidden="true" />
            <p class="text-sm text-slate-500 mt-2">
              Glissez-déposez vos fichiers ici ou
              <span class="text-blue-france font-medium">parcourir</span>
            </p>
            <p class="text-xs text-slate-400 mt-1">PDF, images (PNG, JPG, TIFF)</p>
            <input
              ref="fileInputRef"
              type="file"
              multiple
              accept=".pdf,.png,.jpg,.jpeg,.tiff,.tif"
              class="hidden"
              @change="onFileInput"
            />
          </div>

          <!-- File list -->
          <div v-if="files.length > 0" class="mt-4">
            <p class="text-xs font-medium text-slate-600 mb-2">
              {{ files.length }} fichier{{ files.length > 1 ? 's' : '' }} sélectionné{{ files.length > 1 ? 's' : '' }}
            </p>
            <div class="flex flex-col gap-1.5 max-h-48 overflow-y-auto">
              <div
                v-for="(file, i) in files"
                :key="i"
                class="flex items-center justify-between px-3 py-2 bg-slate-50 rounded-lg text-sm"
              >
                <div class="flex items-center gap-2 min-w-0">
                  <span class="fr-icon-file-line text-slate-400 shrink-0" aria-hidden="true" />
                  <span class="truncate text-slate-700">{{ file.name }}</span>
                  <span class="text-xs text-slate-400 shrink-0">
                    {{ formatSize(file.size) }}
                  </span>
                </div>
                <button
                  class="text-slate-400 hover:text-red-500 transition-colors shrink-0 ml-2"
                  @click="files.splice(i, 1)"
                >
                  <span class="fr-icon-close-line" style="font-size: 14px;" aria-hidden="true" />
                </button>
              </div>
            </div>
          </div>
        </template>

        <!-- After submission: progress tracking -->
        <template v-else>
          <p class="text-sm text-slate-500 mb-4">
            Extraction en cours pour {{ jobs.length }} fichier{{ jobs.length > 1 ? 's' : '' }}.
          </p>

          <div class="flex flex-col gap-3">
            <div
              v-for="job in jobs"
              :key="job.taskId"
              class="px-3 py-3 rounded-lg border"
              :class="jobBorderClass(job)"
            >
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-2 min-w-0">
                  <span class="fr-icon-file-line text-slate-400 shrink-0" aria-hidden="true" />
                  <span class="text-sm text-slate-700 truncate">{{ job.fileName }}</span>
                </div>
                <span class="text-xs font-medium" :class="jobStatusClass(job)">
                  {{ jobStatusLabel(job) }}
                </span>
              </div>

              <div class="h-1.5 bg-slate-200 rounded-full overflow-hidden">
                <div
                  class="h-full transition-all duration-300 rounded-full"
                  :class="job.status === 'failed' ? 'bg-red-500' : job.status === 'completed' ? 'bg-green-500' : 'bg-blue-france'"
                  :style="{ width: `${job.percentage}%` }"
                />
              </div>

              <div v-if="job.status === 'completed' && job.fillingTaskId" class="mt-2 flex justify-end">
                <button
                  class="fr-btn fr-btn--tertiary fr-btn--sm"
                  @click="$router.push(`/${job.fillingTaskId}`)"
                >
                  <span class="fr-icon-eye-line fr-mr-1w" aria-hidden="true" />
                  Voir la tâche
                </button>
              </div>
            </div>
          </div>
        </template>

        <!-- Error -->
        <div v-if="submitError" class="mt-4 p-3 rounded-lg bg-red-50 border border-red-200 text-sm text-red-700">
          {{ submitError }}
        </div>
      </div>

      <!-- Footer -->
      <div class="flex justify-end gap-2 px-6 py-4 border-t border-slate-100">
        <button class="fr-btn fr-btn--tertiary fr-btn--sm" @click="$emit('close')">
          {{ isSubmitted ? 'Fermer' : 'Annuler' }}
        </button>
        <button
          v-if="!isSubmitted"
          class="fr-btn fr-btn--sm"
          :disabled="files.length === 0 || isSubmitting"
          @click="submit"
        >
          <span v-if="isSubmitting" class="fr-icon-loader-line fr-mr-1w" aria-hidden="true" />
          <span v-else class="fr-icon-play-line fr-mr-1w" aria-hidden="true" />
          {{ isSubmitting ? 'Envoi…' : `Lancer (${files.length})` }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTemplatingStore, type TemplatingModel } from '@/stores/templating'
import createHttpClient from '@/api/http-client'
import { OCR_API_URL } from '@/utils/constants'

const http = createHttpClient(OCR_API_URL)

interface JobTrack {
  taskId: string
  fillingTaskId: string | null
  fileName: string
  status: string
  percentage: number
}

const props = defineProps<{
  template: TemplatingModel
}>()

const emit = defineEmits<{
  close: []
}>()

const store = useTemplatingStore()
const router = useRouter()
const files = ref<File[]>([])
const isDragging = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)
const isSubmitting = ref(false)
const isSubmitted = ref(false)
const submitError = ref<string | null>(null)
const jobs = ref<JobTrack[]>([])
let pollTimer: ReturnType<typeof setInterval> | null = null

function onDrop (e: DragEvent) {
  isDragging.value = false
  if (e.dataTransfer?.files) addFiles(e.dataTransfer.files)
}

function onFileInput (e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files) { addFiles(input.files); input.value = '' }
}

function addFiles (fileList: FileList) {
  for (const f of Array.from(fileList)) {
    if (!files.value.some(ex => ex.name === f.name && ex.size === f.size)) {
      files.value.push(f)
    }
  }
}

function formatSize (bytes: number): string {
  if (bytes < 1024) return `${bytes} o`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} Ko`
  return `${(bytes / (1024 * 1024)).toFixed(1)} Mo`
}

async function submit () {
  isSubmitting.value = true
  submitError.value = null
  try {
    const entitiesDefinitions = (props.template.entity_zone ?? [])
      .map(ez => ez.entity_definition)
      .filter(ed => !!ed.definition)

    const parameter = JSON.stringify({
      name: props.template.name,
      definition: `Extraction basée sur le template ${props.template.name}`,
      template_id: props.template.id,
      entities_definitions: entitiesDefinitions,
    })

    const results: JobTrack[] = []
    for (const file of files.value) {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('group_id', props.template.group_id)
      formData.append('task_name', 'tasks.entity_extraction')
      formData.append('parameter', parameter)

      const { data } = await http.post('/jobs/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      results.push({
        taskId: data.id,
        fillingTaskId: null,
        fileName: file.name,
        status: 'queued',
        percentage: 0,
      })
    }
    jobs.value = results
    isSubmitted.value = true
    startPolling()
  }
  catch (e: unknown) {
    submitError.value = (e as Error).message ?? 'Erreur lors de la soumission'
  }
  finally {
    isSubmitting.value = false
  }
}

function startPolling () {
  pollTimer = setInterval(async () => {
    const pending = jobs.value.filter(j => !['completed', 'failed'].includes(j.status))
    if (pending.length === 0) {
      if (pollTimer) clearInterval(pollTimer)
      return
    }
    for (const job of pending) {
      try {
        const { data: tree } = await http.get(`/tasks/${encodeURIComponent(job.taskId)}/tree`)
        if (!Array.isArray(tree) || tree.length === 0) continue

        // Find the filling task in the tree
        const fillingTask = tree.find((t: any) =>
          t.type === 'templating_filling' || t.type === 'tasks.templating_filling',
        )

        // Any task failed?
        const anyFailed = tree.some((t: any) => t.status === 'failed')

        if (anyFailed) {
          job.status = 'failed'
          job.percentage = 100
        } else if (fillingTask) {
          job.fillingTaskId = fillingTask.id
          if (fillingTask.status === 'completed') {
            job.status = 'completed'
            job.percentage = 100
          } else {
            job.status = 'in_progress'
            job.percentage = Math.round((fillingTask.percentage ?? 0) * 100)
          }
        } else {
          // Filling task not yet created — still in progress
          job.status = 'in_progress'
          const root = tree[0]
          job.percentage = Math.min(Math.round((root.percentage ?? 0) * 100), 90)
        }
      } catch {
        // ignore transient errors
      }
    }
  }, 3000)
}

onUnmounted(() => { if (pollTimer) clearInterval(pollTimer) })

function jobStatusLabel (job: JobTrack): string {
  const labels: Record<string, string> = {
    created: 'Créée',
    queued: 'En file',
    started: 'Démarré',
    in_progress: 'En cours',
    completed: 'Terminé',
    failed: 'Échoué',
  }
  return labels[job.status] ?? job.status
}

function jobStatusClass (job: JobTrack): string {
  if (job.status === 'completed') return 'text-green-600'
  if (job.status === 'failed') return 'text-red-600'
  return 'text-slate-500'
}

function jobBorderClass (job: JobTrack): string {
  if (job.status === 'completed') return 'border-green-200 bg-green-50'
  if (job.status === 'failed') return 'border-red-200 bg-red-50'
  return 'border-slate-200 bg-slate-50'
}
</script>
