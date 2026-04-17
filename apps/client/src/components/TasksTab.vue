<template>
  <div class="task-container fr-container">
    <h2 class="fr-h2">Liste des tâches</h2>
    <DsfrButton size="sm" priority="secondary" class="fr-ml-1" @click="statsVisible = true">Voir les statistiques</DsfrButton>

    <table class="fr-table task-table">
      <thead>
        <tr>
          <th style="width:2rem"></th>
          <th @click="sortBy('type')">Tâche ⬍</th>
          <th>Fichier</th>
          <th @click="sortBy('percentage')">Pourcentage ⬍</th>
          <th @click="sortBy('created_at')">Créé le ⬍</th>
          <th @click="sortBy('updated_at')">Mis à jour le ⬍</th>
          <th>Voir résumé</th>
          <th>Supprimer</th>
        </tr>
      </thead>

      <tbody>
        <tr
          v-for="row in flatRows"
          :key="row._rowKey"
          :class="{ 'row-parent': row._isParent, 'row-child': !row._isParent, 'row-empty': row._isEmpty }"
        >
          <td class="expand-cell">
            <button
              v-if="row._isParent"
              class="expand-btn"
              :aria-label="expandedIds.includes(row.id) ? 'Réduire' : 'Développer'"
              @click="toggleExpand(row)"
            >
              <span v-if="loadingChildren.includes(row.id)">⏳</span>
              <span v-else-if="expandedIds.includes(row.id)">▾</span>
              <span v-else>▸</span>
            </button>
            <span v-else class="child-indent">└</span>
          </td>
          <td>
            <span :class="{ 'child-label': !row._isParent }">{{ MapTaskTypeToLabel(row.type) }}</span>
          </td>
          <td>
            <span v-if="row.input?.raw_filename">{{ row.input.raw_filename }}</span>
            <span v-else>—</span>
          </td>
          <td>
            <ProgressBar v-if="!row._isEmpty" :visible="true" :progress="(row.percentage ?? 0) * 100" :text="MapStatusToLabel(row.status)" />
            <span v-else class="no-children">Aucune sous-tâche</span>
          </td>
          <td>{{ row._isEmpty ? '' : formatDate(row.created_at) }}</td>
          <td>{{ row._isEmpty ? '' : formatDate(row.updated_at) }}</td>
          <td>
            <DsfrButton v-if="!row._isEmpty" size="sm" priority="secondary" :disabled="row.status !== 'completed'" @click="goToTask(row)">
              Voir le contenu
            </DsfrButton>
          </td>
          <td>
            <DsfrButton v-if="!row._isEmpty" size="sm" priority="tertiary" @click="removeTask(row.id)">Supprimer</DsfrButton>
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
import { ref, computed, onMounted, onBeforeUnmount, unref } from 'vue'
import { useRouter } from 'vue-router'
import createHttpClient from '@/api/http-client'
import { OCR_API_URL } from '@/utils/constants'
import { useTasksStore } from '@/stores/tasks'
import StatModel from './StatModel.vue'
import ProgressBar from './ProgressBar.vue'

type TaskModel = {
  id: string
  type: string
  status: string
  percentage?: number | null
  parent_id?: string | null
  input?: any
  output?: any
  created_at: number
  updated_at: number
  [k: string]: any
}

type FlatRow = TaskModel & { _rowKey: string; _isParent: boolean; _isEmpty?: boolean }

const store = useTasksStore()
const router = useRouter()
const paginatedData = store.userTasksPaginated

const connectedUsers = ref<number | null>(null)
const http = createHttpClient(OCR_API_URL)

const fetchConnectedUsers = async () => {
  try {
    const { data } = await http.get('/users/count-users-today')
    connectedUsers.value = data?.users_today ?? null
  }
  catch {
    connectedUsers.value = null
  }
}

const data_task_mock = { total: 0, page: 1, page_size: 10, items: [] as TaskModel[] }

// ----- TRI -----
const sortKey = ref('')
const sortAsc = ref(true)

function MapTaskTypeToLabel(type: string) {
  const map: Record<string, string> = {
    ocr: 'OCR',
    default: 'Défaut',
    save_template: 'Modèle',
    forms: 'Formulaires',
    vectorize: 'Vectorisation',
    vlm_ocr: 'VLM OCR',
    page_classification: 'Classification',
    'tasks.page_text_classification': 'Classification texte',
    'tasks.page_classification': 'Classification page',
    'worker.tasks.ocr': 'OCR',
  }
  return map[type] ?? type
}

function MapStatusToLabel(status: string) {
  const map: Record<string, string> = {
    queued: 'En attente',
    in_progress: 'En cours',
    started: 'Démarré',
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

// ----- TREE -----
const expandedIds = ref<string[]>([])
const loadingChildren = ref<string[]>([])
const childrenCache = ref<Record<string, TaskModel[]>>({})

async function toggleExpand(task: TaskModel) {
  const id = task.id
  if (expandedIds.value.includes(id)) {
    expandedIds.value = expandedIds.value.filter(x => x !== id)
    return
  }
  if (!(id in childrenCache.value)) {
    loadingChildren.value = [...loadingChildren.value, id]
    try {
      const children = await store.fetchTaskChildren(id)
      childrenCache.value = { ...childrenCache.value, [id]: children }
    } catch (e) {
      console.error('Failed to fetch children for', id, e)
    } finally {
      loadingChildren.value = loadingChildren.value.filter(x => x !== id)
    }
  }
  expandedIds.value = [...expandedIds.value, id]
}

const paginatedTasks = computed(() => {
  const resolved = unref(paginatedData)
  const items = resolved?.items ?? []
  if (!sortKey.value) return items
  return [...items].sort((a: any, b: any) => {
    const valA = a[sortKey.value]
    const valB = b[sortKey.value]
    if (valA === valB) return 0
    return sortAsc.value ? (valA > valB ? 1 : -1) : (valA < valB ? 1 : -1)
  })
})

const rootTasks = computed((): TaskModel[] => {
  const items = paginatedTasks.value || []
  const roots = items.filter((t: TaskModel) => !t.parent_id)
  return roots.length > 0 ? roots : data_task_mock.items
})

const flatRows = computed((): FlatRow[] => {
  const rows: FlatRow[] = []
  for (const task of rootTasks.value) {
    rows.push({ ...task, _rowKey: task.id, _isParent: true })
    if (expandedIds.value.includes(task.id)) {
      const children = childrenCache.value[task.id] ?? []
      if (children.length === 0) {
        rows.push({ ...task, _rowKey: `${task.id}__empty`, _isParent: false, _isEmpty: true })
      } else {
        for (const child of children) {
          rows.push({ ...child, _rowKey: `${task.id}__${child.id}`, _isParent: false })
        }
      }
    }
  }
  return rows
})

const paginatedDataSafe = computed(() => {
  const resolved = unref(paginatedData)
  if ((resolved?.items ?? []).length > 0) return resolved
  return data_task_mock
})

const loadPage = async (page = 1, overridePageSize?: number) => {
  const pageSize = overridePageSize ?? unref(paginatedData)?.page_size ?? 10
  await store.fetchUserTasks(page, pageSize)
  expandedIds.value = []
  childrenCache.value = {}
  try { await fetchConnectedUsers() } catch { }
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
const statsVisible = ref(false)

const goToTask = (task: any) => {
  if (!task || !task.id) return
  router.push(`/${task.id}`)
}

const removeTask = async (taskId: string) => {
  if (!taskId) return
  try {
    await store.deleteTask(taskId)
    const resolved = unref(paginatedData)
    await loadPage(resolved?.page ?? 1, resolved?.page_size ?? 10)
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
  } catch { return String(ts) }
}

</script>

<style scoped>
.task-container {
  padding: 20px;
  position: relative;
}

.task-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.task-table th,
.task-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: center;
  overflow-wrap: anywhere;
  word-break: break-word;
  white-space: normal;
}

.task-table th { cursor: pointer; }

.row-child { background-color: #f5f7ff; }
.row-child td { border-left: 3px solid #0b6bff; }
.row-empty td { color: #999; font-style: italic; }
.child-label { font-size: 0.875rem; color: #444; }

.expand-cell { width: 2rem; text-align: center; padding: 4px; }
.expand-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  padding: 2px 4px;
  border-radius: 4px;
  line-height: 1;
  transition: background 0.15s;
}
.expand-btn:hover { background: #e8f0fe; }
.child-indent { color: #0b6bff; font-size: 1rem; }
.no-children { color: #888; font-style: italic; }

.pagination {
  margin-top: 15px;
  display: flex;
  justify-content: center;
  gap: 15px;
}

.modal-overlay {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal {
  background: white;
  padding: 1.25rem;
  border-radius: 12px;
  width: min(900px, 95%);
  max-height: 80vh;
  overflow: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
  z-index: 10000;
}

.modal .modal-header,
.modal .modal-section { padding-left: 1rem; padding-right: 1rem; }

.extracted-text { width: 100%; min-height: 6rem; resize: vertical; box-sizing: border-box; padding: 0.5rem; }

.modal-header { display: flex; justify-content: space-between; align-items: center; gap: 1rem; margin-bottom: 0.5rem; }
.modal-section { border-top: 1px solid #eee; padding: 0.75rem 0; }
.section-title { font-weight: 600; margin-bottom: 0.5rem; }
.section-content { display: block; }
.modal-actions .section-content > * { margin-right: 0.5rem; }
.copy-success { color: #0b6623; margin-left: 0.75rem; font-weight: 600; }

.connected-badge {
  position: absolute; right: 12px; bottom: 12px;
  background: #0b6bff; color: white;
  padding: 6px 10px; border-radius: 999px;
  display: flex; align-items: center; gap: 8px;
  box-shadow: 0 6px 18px rgba(11, 107, 255, 0.15);
  font-weight: 600;
}
.connected-badge .badge-emoji { font-size: 14px; }
.connected-badge .badge-number { min-width: 32px; text-align: center; }
</style>
