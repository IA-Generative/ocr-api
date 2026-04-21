import type { components } from '@/api/types/api.schema'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import createHttpClient from '@/api/http-client'
import { OCR_API_URL } from '@/utils/constants'

type TaskModel = components['schemas']['TaskModel']

const http = createHttpClient(OCR_API_URL)

export const useTasksStore = defineStore('tasks', () => {
  // paginated shape: { items: TaskModel[], page, page_size, total }
  const userTasksPaginated = ref<{ items: TaskModel[]; page: number; page_size: number; total: number } | any>({ items: [], page: 1, page_size: 10, total: 0 })
  const loading = ref(false)
  const error = ref<string | undefined>(undefined)

  async function fetchUserTasks (page = 1, page_size = 10) {
    loading.value = true
    try {
      const { data } = await http.get(`/tasks/user/`, { params: { page: page, limit: page_size } })
      userTasksPaginated.value.total = data.total ?? 0
      userTasksPaginated.value.page = data.page ?? page
      userTasksPaginated.value.page_size = data.page_size ?? page_size
      userTasksPaginated.value.items = data.items ?? []
    }
    catch (err: any) {
      // keep existing behavior: swallow errors here (UI may show nothing)
    }
    finally {
      loading.value = false
    }
  }

  async function fetchTaskChildren (taskId: string): Promise<TaskModel[]> {
    try {
      const { data } = await http.get(`/tasks/${encodeURIComponent(taskId)}/children`)
      return data ?? []
    }
    catch {
      return []
    }
  }

  async function fetchTaskTree (taskId: string): Promise<TaskModel[]> {
    try {
      const { data } = await http.get(`/tasks/${encodeURIComponent(taskId)}/tree`)
      return data ?? []
    }
    catch {
      return []
    }
  }

  async function deleteTask (taskId: string) {
    if (!taskId) throw new Error('taskId required')
    await http.delete(`/tasks/${encodeURIComponent(taskId)}`)
    // remove locally if present
    const items = userTasksPaginated.value?.items ?? []
    userTasksPaginated.value = { ...userTasksPaginated.value, items: items.filter((t: any) => t.id !== taskId), total: Math.max(0, (userTasksPaginated.value.total || items.length) - 1) }
  }

  async function revokeTask (taskId: string) {
    if (!taskId) throw new Error('taskId required')
    await http.delete(`/v1/tasks/revoke/${encodeURIComponent(taskId)}`)
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
    fetchTaskChildren,
    fetchTaskTree,
    deleteTask,
    revokeTask,
    stopPollingUserTasks,
  }
})
