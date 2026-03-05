import type { components } from '@/api/types/api.schema'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import createHttpClient from '@/api/http-client'
import { OCR_API_URL } from '@/utils/constants'
import useToaster from '@/composables/use-toaster'

type TaskModel = components['schemas']['TaskModel']

const http = createHttpClient(OCR_API_URL)
const { addErrorMessage, addSuccessMessage } = useToaster()

export const useTasksStore = defineStore('tasks', () => {
  // paginated shape: { items: TaskModel[], page, page_size, total }
  const userTasksPaginated = ref<{ items: TaskModel[]; page: number; page_size: number; total: number } | any>({ items: [], page: 1, page_size: 10, total: 0 })
  const loading = ref(false)
  const error = ref<string | undefined>(undefined)

  async function fetchUserTasks (page = 1, pageSize = 10) {
    loading.value = true
    error.value = undefined
    try {
      const { data } = await http.get('/tasks/user/', { params: { page, page_size: pageSize } })
      // Expecting API to return a paginated object { items, page, page_size, total }
      // If it returns an array, normalize to that shape. Also normalize each task item.
      const normalizeTask = (t: any) => ({
        id: t.id,
        user_id: t.user_id,
        type: t.type,
        status: t.status ?? 'queued',
        percentage: typeof t.percentage === 'number' ? t.percentage : (t.percentage ? Number(t.percentage) : 0),
        input: t.input ?? null,
        output: t.output ?? null,
        created_at: typeof t.created_at === 'number' ? t.created_at : (t.created_at ? Number(t.created_at) : 0),
        updated_at: typeof t.updated_at === 'number' ? t.updated_at : (t.updated_at ? Number(t.updated_at) : 0),
        extras: t.extras ?? null,
        position: typeof t.position === 'number' ? t.position : (t.position ? Number(t.position) : null),
        content_hash: t.content_hash ?? null,
      })

      if (Array.isArray(data)) {
        userTasksPaginated.value = { items: data.map(normalizeTask), page, page_size: pageSize, total: data.length }
      }
      else {
        const pag = data || { items: [], page, page_size: pageSize, total: 0 }
        pag.items = (pag.items || []).map(normalizeTask)
        userTasksPaginated.value = pag
      }
      return userTasksPaginated.value
    }
    catch (err: any) {
      error.value = err?.message ?? 'Erreur lors de la récupération des tâches.'
      addErrorMessage({ title: 'Erreur :', description: error.value })
      throw err
    }
    finally {
      loading.value = false
    }
  }

  async function deleteTask (taskId: string) {
    if (!taskId) throw new Error('taskId required')
    try {
      // Attempt to delete; API may not support delete — handle errors gracefully
      await http.delete(`/tasks/${encodeURIComponent(taskId)}`)
      addSuccessMessage({ title: 'Supprimé', description: `Tâche ${taskId} supprimée` })
      // remove locally if present
      const items = userTasksPaginated.value?.items ?? []
      userTasksPaginated.value = { ...userTasksPaginated.value, items: items.filter((t: any) => t.id !== taskId), total: Math.max(0, (userTasksPaginated.value.total || items.length) - 1) }
    }
    catch (err: any) {
      addErrorMessage({ title: 'Erreur :', description: `Impossible de supprimer la tâche: ${err?.message ?? err}` })
      throw err
    }
  }

  function stopPollingUserTasks () {
    // Placeholder for compatibility with other code that may call stopPollingUserTasks
    // No-op for now.
  }

  return {
    userTasksPaginated,
    loading,
    error,
    fetchUserTasks,
    deleteTask,
    stopPollingUserTasks,
  }
})
