<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import createHttpClient from '@/api/http-client'
import { useTasksStore } from '@/stores/tasks'
import { OCR_API_URL } from '@/utils/constants'
import ProgressBar from './ProgressBar.vue'

const store = useTasksStore()
const router = useRouter()
const http = createHttpClient(OCR_API_URL)

// ----- TRI -----
const sortKey = ref('created_at')
const sortAsc = ref(false)

function goToDetail (taskId: string) {
  router.push(`/tasks/${taskId}`)
}

function MapStatusToLabel (status: string) {
  const map: Record<string, string> = {
    queued: 'En attente',
    in_progress: 'En cours',
    completed: 'Terminé',
    failed: 'Échoué',
  }
  return map[status] || status
}

function sortBy (key: string) {
  if (sortKey.value === key) {
    sortAsc.value = !sortAsc.value
  } else {
    sortKey.value = key
    sortAsc.value = true
  }
}

const sortedTasks = computed(() => {
  const items: any[] = store.userTasksPaginated?.items ?? []
  if (!sortKey.value) {
    return items
  }
  return [...items].sort((a, b) => {
    const valA = a[sortKey.value]
    const valB = b[sortKey.value]
    if (valA === valB) {
      return 0
    }
    if (sortAsc.value) {
      return valA > valB ? 1 : -1
    }
    return valA < valB ? 1 : -1
  })
})

async function loadAll () {
  await store.fetchUserTasks(1, 1000)
}

onMounted(() => {
  void loadAll()
})

onBeforeUnmount(() => {
  if (typeof store.stopPollingUserTasks === 'function') {
    store.stopPollingUserTasks()
  }
})

// ----- TÉLÉCHARGEMENT -----
async function downloadTaskResult (task: any) {
  if (!task || task.status !== 'completed') {
    return
  }
  try {
    const { data: text } = await http.get<string>(`/text-task/${encodeURIComponent(task.id)}`, {
      headers: { accept: 'text/plain' },
    })
    const blob = new Blob([text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    const baseName = task.input?.raw_filename
      ? task.input.raw_filename.replace(/\.[^/.]+$/, '')
      : `ocr-output-${task.id}`
    a.download = `${baseName}.txt`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  } catch (e) {
    console.error('Téléchargement échoué', e)
  }
}

// ----- SUPPRESSION -----
async function removeTask (taskId: string) {
  if (!taskId) {
    return
  }
  try {
    await store.deleteTask(taskId)
  } catch {
    // store already shows error toast
  }
}

function formatDate (ts: any) {
  if (ts === null || ts === undefined || ts === '') {
    return ''
  }
  try {
    let n = Number(ts)
    if (Number.isNaN(n)) {
      return String(ts)
    }
    if (n < 1e12) {
      n = n * 1000
    }
    return new Date(n).toLocaleString()
  } catch {
    return String(ts)
  }
}
</script>

<template>
  <div class="task-container fr-container">
    <h2 class="fr-h2">
      Liste des tâches
    </h2>

    <div class="table-responsive">
      <table class="fr-table task-table">
        <thead>
          <tr>
            <th @click="sortBy('type')">
              Type ⬍
            </th>
            <th @click="sortBy('percentage')">
              Pourcentage ⬍
            </th>
            <th @click="sortBy('created_at')">
              Créé le ⬍
            </th>
            <th @click="sortBy('updated_at')">
              Mis à jour le ⬍
            </th>
            <th>Détail</th>
            <th>Voir résultat</th>
            <th>Supprimer</th>
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="task in sortedTasks"
            :key="task.id"
          >
            <td>
              <span v-if="task.input?.raw_filename">{{ task.input.raw_filename }}</span>
              <span v-else>Inconnu</span>
            </td>

            <td>
              <ProgressBar
                :visible="true"
                :progress="(task.percentage ?? 0) * 100"
                :text="MapStatusToLabel(task.status)"
              />
            </td>

            <td>{{ formatDate(task.created_at) }}</td>
            <td>{{ formatDate(task.updated_at) }}</td>

            <td>
              <DsfrButton
                size="sm"
                priority="tertiary"
                @click="goToDetail(task.id)"
              >
                Voir le détail
              </DsfrButton>
            </td>

            <td>
              <DsfrButton
                size="sm"
                priority="secondary"
                :disabled="task.status !== 'completed'"
                @click="downloadTaskResult(task)"
              >
                Voir résultat
              </DsfrButton>
            </td>

            <td>
              <DsfrButton
                size="sm"
                priority="tertiary"
                @click="removeTask(task.id)"
              >
                Supprimer
              </DsfrButton>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.task-container {
  padding: 20px;
}

.table-responsive {
  width: 100%;
  overflow-x: auto;
}

.task-table {
  width: 100%;
  min-width: 600px;
  border-collapse: collapse;
  table-layout: auto;
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

.task-table th {
  cursor: pointer;
}
</style>
