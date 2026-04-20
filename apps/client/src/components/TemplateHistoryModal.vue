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
          <h2 class="text-base font-semibold text-slate-800">Historique des extractions</h2>
          <p class="text-xs text-slate-400 mt-0.5">Template : {{ templateName }} · {{ total }} résultat{{ total > 1 ? 's' : '' }}</p>
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
      <div class="flex-1 overflow-y-auto px-6 py-4">
        <div v-if="isLoading" class="flex items-center justify-center py-12 text-slate-400">
          <span class="fr-icon-loader-line animate-spin mr-2" aria-hidden="true" />
          Chargement…
        </div>

        <div v-else-if="tasks.length === 0" class="flex flex-col items-center justify-center py-12 text-slate-400 gap-2">
          <span class="fr-icon-file-text-line" style="font-size: 28px;" aria-hidden="true" />
          <p class="text-sm">Aucune extraction pour ce template.</p>
        </div>

        <div v-else class="flex flex-col gap-2">
          <div
            v-for="task in tasks"
            :key="task.id"
            class="flex items-center gap-3 px-3 py-2.5 rounded-lg border transition-colors"
            :class="borderClass(task.status)"
          >
            <!-- Status dot -->
            <span
              class="shrink-0 w-2.5 h-2.5 rounded-full"
              :class="dotClass(task.status)"
            />

            <!-- File info -->
            <div class="flex-1 min-w-0">
              <p class="text-sm text-slate-700 font-medium truncate" :title="task.fileName">{{ task.fileName }}</p>
              <p class="text-xs text-slate-400">
                {{ formatDate(task.createdAt) }}
                <span class="ml-2" :class="statusColor(task.status)">{{ statusLabel(task.status) }}</span>
              </p>
            </div>

            <!-- Actions -->
            <div class="flex items-center gap-1.5 shrink-0">
              <button
                v-if="task.hasResultFile"
                class="inline-flex items-center gap-1 rounded-md bg-blue-600 px-2 py-1 text-xs font-medium text-white hover:bg-blue-700 transition-colors"
                title="Télécharger le document rempli"
                @click="ocrStore.downloadResultFile(task.id)"
              >
                <span class="fr-icon-download-line" style="font-size: 12px;" aria-hidden="true" />
                Télécharger
              </button>
              <button
                class="inline-flex items-center gap-1 rounded-md border border-slate-200 px-2 py-1 text-xs text-slate-600 hover:bg-slate-50 transition-colors"
                title="Voir la tâche"
                @click="$router.push(`/${task.id}`)"
              >
                <span class="fr-icon-eye-line" style="font-size: 12px;" aria-hidden="true" />
                Voir
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer with pagination -->
      <div class="flex items-center justify-between px-6 py-3 border-t border-slate-100">
        <p class="text-xs text-slate-400">
          {{ (currentPage - 1) * pageSize + 1 }}–{{ Math.min(currentPage * pageSize, total) }} sur {{ total }}
        </p>
        <div class="flex items-center gap-1">
          <button
            class="fr-btn fr-btn--tertiary-no-outline fr-btn--sm"
            :disabled="currentPage <= 1"
            @click="goPage(-1)"
          >
            <span class="fr-icon-arrow-left-s-line" aria-hidden="true" />
          </button>
          <span class="text-xs text-slate-500 px-2">{{ currentPage }} / {{ totalPages }}</span>
          <button
            class="fr-btn fr-btn--tertiary-no-outline fr-btn--sm"
            :disabled="currentPage >= totalPages"
            @click="goPage(1)"
          >
            <span class="fr-icon-arrow-right-s-line" aria-hidden="true" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useOcrStore } from '@/stores/ocr'
import createHttpClient from '@/api/http-client'
import { OCR_API_URL } from '@/utils/constants'

const http = createHttpClient(OCR_API_URL)
const ocrStore = useOcrStore()

interface FillingTask {
  id: string
  status: string
  fileName: string
  createdAt: number
  hasResultFile: boolean
}

const props = defineProps<{
  templateId: string
  templateName: string
}>()

defineEmits<{ close: [] }>()

const tasks = ref<FillingTask[]>([])
const allTasks = ref<FillingTask[]>([])
const currentPage = ref(1)
const pageSize = 10
const isLoading = ref(false)

const total = computed(() => allTasks.value.length)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

onMounted(() => fetchAll())

async function fetchAll () {
  isLoading.value = true
  try {
    // Fetch all user tasks and filter by template_id
    let page = 1
    let hasMore = true
    const matched: FillingTask[] = []
    while (hasMore) {
      const { data } = await http.get('/tasks/user/', { params: { page, page_size: 50 } })
      const items = data.items ?? []
      for (const task of items) {
        if (task.parameters?.template_id !== props.templateId) continue
        try {
          const { data: tree } = await http.get(`/tasks/${encodeURIComponent(task.id)}/tree`)
          const filling = (tree as any[]).find((t: any) =>
            t.type === 'templating_filling' || t.type === 'tasks.templating_filling',
          )
          matched.push({
            id: filling?.id ?? task.id,
            status: filling?.status ?? task.status,
            fileName: task.input?.raw_filename ?? task.id,
            createdAt: task.created_at,
            hasResultFile: !!filling?.output?.result_path,
          })
        } catch {
          matched.push({
            id: task.id,
            status: task.status,
            fileName: task.input?.raw_filename ?? task.id,
            createdAt: task.created_at,
            hasResultFile: false,
          })
        }
      }
      hasMore = items.length === 50 && page * 50 < (data.total ?? 0)
      page++
    }
    allTasks.value = matched.sort((a, b) => b.createdAt - a.createdAt)
    updatePage()
  } catch {
    allTasks.value = []
    tasks.value = []
  } finally {
    isLoading.value = false
  }
}

function updatePage () {
  const start = (currentPage.value - 1) * pageSize
  tasks.value = allTasks.value.slice(start, start + pageSize)
}

function goPage (dir: number) {
  currentPage.value += dir
  updatePage()
}

function formatDate (ts: number): string {
  return new Date(ts * 1000).toLocaleString('fr-FR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function statusLabel (status: string): string {
  const labels: Record<string, string> = {
    completed: 'Terminé',
    failed: 'Échoué',
    queued: 'En file',
    started: 'Démarré',
    in_progress: 'En cours',
  }
  return labels[status] ?? status
}

function statusColor (status: string): string {
  if (status === 'completed') return 'text-green-600'
  if (status === 'failed') return 'text-red-600'
  return 'text-amber-600'
}

function dotClass (status: string): string {
  if (status === 'completed') return 'bg-green-500'
  if (status === 'failed') return 'bg-red-500'
  return 'bg-amber-400'
}

function borderClass (status: string): string {
  if (status === 'completed') return 'border-green-200 bg-green-50/50'
  if (status === 'failed') return 'border-red-200 bg-red-50/50'
  return 'border-slate-200 bg-slate-50/50'
}
</script>
