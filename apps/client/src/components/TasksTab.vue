<template>
  <div class="task-container fr-container">
    <h2 class="fr-h2">Liste des tâches</h2>
    <DsfrButton size="sm" priority="secondary" class="fr-ml-1" @click="statsVisible = true">Voir les statistiques</DsfrButton>

    <table class="fr-table task-table">
      <thead>
        <tr>
          <th @click="sortBy('type')">Type ⬍</th>
          <th @click="sortBy('percentage')">Pourcentage ⬍</th>
          <th @click="sortBy('created_at')">Créé le ⬍</th>
          <th @click="sortBy('updated_at')">Mis à jour le ⬍</th>
          <th>Voir résumé</th>
          <th>Supprimer</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="task in displayedTasks" :key="task.id">
          <td>
            <span v-if="task.input?.raw_filename">{{ task.input.raw_filename }}</span>
            <span v-else>Inconnu</span>
          </td>

          <td>
            <ProgressBar :visible="true" :progress="(task.percentage ?? 0) * 100" :text="MapStatusToLabel(task.status)" />
          </td>

          <td>{{ formatDate(task.created_at) }}</td>
          <td>{{ formatDate(task.updated_at) }}</td>

          <td>
            <DsfrButton size="sm" priority="secondary" :disabled="task.status !== 'completed'" @click="openModal(task)">
              Voir le contenu
            </DsfrButton>
          </td>

          <td>
            <DsfrButton size="sm" priority="tertiary" @click="removeTask(task.id)">Supprimer</DsfrButton>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Pagination -->
    <div class="pagination fr-mt-2">
      <DsfrButton size="sm" priority="tertiary" :disabled="paginatedDataSafe.page === 1" @click="loadPage(paginatedDataSafe.page - 1)">
        Précédent
      </DsfrButton>

      <span class="fr-ml-2 fr-mr-2">Page {{ paginatedDataSafe.page }} / {{ totalPages }}</span>

      <DsfrButton size="sm" priority="tertiary" :disabled="paginatedDataSafe.page === totalPages" @click="loadPage(paginatedDataSafe.page + 1)">
        Suivant
      </DsfrButton>
    </div>

    <!-- Modal -->
    <div v-if="selectedTask" class="modal-overlay" @click.self="selectedTask = null">
      <div class="modal fr-card" @click.stop>
        <header class="modal-header fr-card">
          <h3 class="fr-h3">Résumer</h3>  
        </header>


        <section class="modal-section fr-card">
          <div class="section-title">Source</div>
          <div class="section-content">
            <div v-if="selectedTask.input?.url">
              <a :href="selectedTask.input.url" target="_blank" rel="noopener noreferrer">{{ selectedTask.input.url }}</a>
            </div>
            <div v-else-if="selectedTask.input?.raw_filename">{{ selectedTask.input.raw_filename }}</div>
            <div v-else>—</div>
          </div>
        </section>

        <section class="modal-section fr-card">
          <div class="section-title">Contenu</div>
          <div class="section-content">
            <div v-if="selectedTask.output?.text">
              <textarea readonly class="extracted-text" :value="selectedTask.output.text"></textarea>
            </div>
            <div v-else>
              <div>Contenu indisponible</div>
            </div>
          </div>
        </section>

        <section class="modal-section modal-actions">
          <div class="section-content">
            <DsfrButton v-if="selectedTask.output?.text" size="sm" priority="tertiary" @click="copyToClipboard(selectedTask.output.text)">Copier le contenu</DsfrButton>
            <DsfrButton v-else-if="selectedTask.input?.raw_filename" size="sm" priority="tertiary" @click="copyToClipboard(selectedTask.input.raw_filename)">Copier le nom</DsfrButton>
            <span v-if="copySuccess" class="copy-success">Copié&nbsp;!</span>
          </div>
        </section>

      </div>
    </div>
    
    <!-- Stats Modal -->
    <StatModel v-if="statsVisible" @close="statsVisible = false" />

      <!-- Connected users badge -->
      <div class="connected-badge" title="Utilisateurs qu'ont utilisé le service aujourd'hui">
        <span class="badge-emoji">👥</span>
        <span class="badge-number">{{ connectedUsers ?? '—' }}</span>
      </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import createHttpClient from '@/api/http-client'
import { OCR_API_URL } from '@/utils/constants'
import { useTasksStore } from '@/stores/tasks'
import StatModel from './StatModel.vue'
import ProgressBar from './ProgressBar.vue'

const store = useTasksStore()
const router = useRouter()
const paginatedData = store.userTasksPaginated

// connected users today badge
const connectedUsers = ref<number | null>(null)
const http = createHttpClient(OCR_API_URL)

const fetchConnectedUsers = async () => {
  try {
    const { data } = await http.get('/users/count-users-today')
    connectedUsers.value = data?.users_today ?? null
  }
  catch (e) {
    connectedUsers.value = null
  }
}


const data_task_mock = {"total": 0, "page": 1, "page_size": 10, "items": []}


// ----- TRI -----
const sortKey = ref('')
const sortAsc = ref(true)

function MapStatusToLabel(status: string) {
  const map: Record<string,string> = {
    queued: 'En attente',
    in_progress: 'En cours',
    completed: 'Terminé',
    failed: 'Échoué',
  }
  return map[status] || status
}

function sortBy(key: string) {
  if (sortKey.value === key) {
    sortAsc.value = !sortAsc.value
  } else {
    sortKey.value = key
    sortAsc.value = true
  }
}

const paginatedTasks = computed(() => {
  const resolved = paginatedData && Object.prototype.hasOwnProperty.call(paginatedData, 'value')
    ? paginatedData.value
    : paginatedData
  console.log('Resolved paginated data for sorting:', resolved)
  const items = resolved?.items ?? []
  if (!sortKey.value) return items
  return [...items].sort((a: any, b: any) => {
    const key = sortKey.value
    const valA = a[key]
    const valB = b[key]
    if (valA === valB) return 0
    return sortAsc.value ? (valA > valB ? 1 : -1) : (valA < valB ? 1 : -1)
  })
})

// If API returns no tasks, use the provided mock so the table is visible for dev
const displayedTasks = computed(() => {
  const items = paginatedTasks.value || []
  if (items.length > 0) return items
  return (data_task_mock?.items ?? [])
})

const paginatedDataSafe = computed(() => {
  const resolved = paginatedData && Object.prototype.hasOwnProperty.call(paginatedData, 'value')
    ? paginatedData.value
    : paginatedData
  if ((resolved?.items ?? []).length > 0) return resolved
  return data_task_mock
})

const loadPage = async (page = 1, overridePageSize?: number) => {
  const pageSize = overridePageSize ?? paginatedData?.page_size ?? 10
  await store.fetchUserTasks(page, pageSize)
  try { await fetchConnectedUsers() } catch (e) { }
}

onMounted(() => {
  void loadPage(1)
  void fetchConnectedUsers()
})

onBeforeUnmount(() => {
  if (typeof store.stopPollingUserTasks === 'function') {
    store.stopPollingUserTasks()
  }
})

const totalPages = computed(() => {
  const resolved = paginatedDataSafe.value || {}
  const total = resolved.total ?? 0
  const pageSize = resolved.page_size ?? 1
  return Math.max(1, Math.ceil(total / pageSize))
})

// ----- MODAL -----
const selectedTask = ref<any|null>(null)
const statsVisible = ref(false)

const openModal = (task: any) => {
  if (!task || task.status !== 'completed') return
  router.push(`/${task.id}`)
}

const removeTask = async (taskId: string) => {
  if (!taskId) return
  try {
    await store.deleteTask(taskId)
    const currentPage = paginatedData && paginatedData.value ? paginatedData.value.page ?? 1 : (paginatedData.page ?? 1)
    const pageSize = paginatedData && paginatedData.value ? paginatedData.value.page_size ?? 10 : (paginatedData.page_size ?? 10)
    await loadPage(currentPage, pageSize)
  }
  catch (e) {
    console.error('Failed to remove task', e)
  }
}

const formatDate = (ts: any) => {
  if (ts === null || ts === undefined || ts === '') return ''
  try {
    let n = Number(ts)
    if (Number.isNaN(n)) return String(ts)
    if (n < 1e12) n = n * 1000
    return new Date(n).toLocaleString()
  } catch (e) { return String(ts) }
}

const copySuccess = ref(false)
let _copyTimeout: any = null

const copyToClipboard = async (text: string) => {
  try {
    if (navigator && (navigator as any).clipboard && (navigator as any).clipboard.writeText) {
      await (navigator as any).clipboard.writeText(text)
    } else {
      const ta = document.createElement('textarea')
      ta.value = text
      ta.style.position = 'fixed'
      ta.style.opacity = '0'
      document.body.appendChild(ta)
      ta.focus()
      ta.select()
      document.execCommand('copy')
      document.body.removeChild(ta)
    }

    copySuccess.value = true
    if (_copyTimeout) clearTimeout(_copyTimeout)
    _copyTimeout = setTimeout(() => (copySuccess.value = false), 2000)
  } catch (e) { console.error('Copy failed', e) }
}

const _escHandler = (e: KeyboardEvent) => {
  if (e.key === 'Escape' || e.key === 'Esc') selectedTask.value = null
}

onMounted(() => { window.addEventListener('keydown', _escHandler) })
onBeforeUnmount(() => { window.removeEventListener('keydown', _escHandler); if (_copyTimeout) clearTimeout(_copyTimeout) })
</script>

<style scoped>
/* (Keep the styles from the user's template) */
.task-container {
  padding: 20px;
  position: relative;
}

.task-table {
  width: 100%;
  border-collapse: collapse;
}

.task-table {
  table-layout: fixed;
}

.task-table th,
.task-table td {
  overflow-wrap: anywhere;
  word-break: break-word;
  white-space: normal;
}

.task-table th,
.task-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: center;
  cursor: pointer;
}

.pagination {
  margin-top: 15px;
  display: flex;
  justify-content: center;
  gap: 15px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);

  display: flex;
  justify-content: center;
  align-items: center;
}

.modal {
  background: white;
  padding: 1.25rem;
  border-radius: 12px;
  width: min(900px, 95%);
  max-width: 900px;
  max-height: 80vh;
  overflow: auto;
  box-sizing: border-box;
  box-shadow: 0 10px 30px rgba(0,0,0,0.25);
  z-index: 10000;
}

.modal .modal-header,
.modal .modal-section,
.modal .modal-footer {
  padding-left: 1rem;
  padding-right: 1rem;
}

.extracted-text {
  width: 100%;
  min-height: 6rem;
  resize: vertical;
  box-sizing: border-box;
  padding: 0.5rem;
}

.summary-block { margin-top: 1rem }
.summary-block > div { max-height: 50vh; overflow: auto; padding-right: 0.5rem }

.modal-header { display:flex; justify-content:space-between; align-items:center; gap:1rem; margin-bottom:0.5rem }
.modal-close { background:transparent; border:none; font-size:1.25rem; cursor:pointer }
.modal-section { border-top:1px solid #eee; padding:0.75rem 0 }
.section-title { font-weight:600; margin-bottom:0.5rem }
.section-content { display:block }
.extracted-text { width:100%; min-height:6rem; resize:vertical }
.modal-actions .section-content > * { margin-right:0.5rem }
.modal-meta .meta-grid { display:grid; grid-template-columns: repeat(2, 1fr); gap:0.5rem 1rem }
.modal-footer { margin-top:1rem; display:flex; justify-content:flex-end }
.copy-success { color:#0b6623; margin-left:0.75rem; font-weight:600 }

.connected-badge { position:absolute; right:12px; bottom:12px; background:#0b6bff; color:white; padding:6px 10px; border-radius:999px; display:flex; align-items:center; gap:8px; box-shadow:0 6px 18px rgba(11,107,255,0.15); font-weight:600 }
.connected-badge .badge-emoji { font-size:14px }
.connected-badge .badge-number { min-width:32px; text-align:center }
</style>
