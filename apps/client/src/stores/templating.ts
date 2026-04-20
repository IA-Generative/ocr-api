import { defineStore } from 'pinia'
import { ref } from 'vue'
import createHttpClient from '@/api/http-client'
import { OCR_API_URL } from '@/utils/constants'

const http = createHttpClient(OCR_API_URL)

export interface EntityDefinitionData {
  name: string
  definition: string | null
  entity_type: string
  formats: string[]
  exemples: string[]
}

export interface EntityZoneData {
  entity_definition: EntityDefinitionData
  boxes: unknown | null
}

export interface ExtractionResult {
  valid_fields: string[]
  invalid_fields: string[]
}

export interface TemplatingModel {
  id: string
  name: string
  description: string
  user_id: string | null
  group_id: string
  source_file: string
  source_task_id: string | null
  extracting_status: string | null
  total_page: number
  created_at: number
  updated_at: number
  entity_zone: EntityZoneData[] | null
  entity_names: ExtractionResult | null
  extras: Record<string, unknown> | null
}

export interface TemplatingListResponse {
  items: TemplatingModel[]
  total: number
  page: number
  page_size: number
}

export interface TaskInfo {
  id: string
  status: string
  percentage: number | null
}

export const useTemplatingStore = defineStore('templating', () => {
  const templatings = ref<TemplatingModel[]>([])
  const total = ref(0)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  // task info keyed by templating id
  const taskInfos = ref<Record<string, TaskInfo>>({})

  async function fetchTaskInfo (templatingId: string): Promise<void> {
    try {
      const { data } = await http.get(`/tasks/${encodeURIComponent(templatingId)}`)
      const task = Array.isArray(data) ? data[0] : data
      if (task) {
        taskInfos.value[templatingId] = { id: task.id, status: task.status, percentage: task.percentage ?? null }
      }
    }
    catch {
      // task may not exist yet
    }
  }

  async function fetchAllTaskInfos (): Promise<void> {
    await Promise.all(templatings.value.map((t: TemplatingModel) => fetchTaskInfo(t.id)))
  }

  async function uploadTemplating (
    file: File,
    name: string,
    description: string,
    groupId: string = 'DEFAULT',
  ): Promise<TemplatingModel> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('name', name)
    formData.append('description', description)
    formData.append('group_id', groupId)

    const { data } = await http.post<TemplatingModel>('/v1/templatings/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    templatings.value.unshift(data)
    total.value += 1
    return data
  }

  async function fetchTemplatings (page = 1, pageSize = 20): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const { data } = await http.get<TemplatingListResponse>('/v1/templatings/', {
        params: { page, page_size: pageSize },
      })
      templatings.value = data.items
      total.value = data.total
      // fetch task status for each templating
      await Promise.all(data.items.map((t: TemplatingModel) => fetchTaskInfo(t.id)))
    }
    catch (e: unknown) {
      error.value = (e as Error).message ?? 'Erreur lors du chargement des templates'
    }
    finally {
      isLoading.value = false
    }
  }

  async function deleteTemplating (id: string): Promise<void> {
    await http.delete(`/v1/templatings/${id}`)
    templatings.value = templatings.value.filter((t: TemplatingModel) => t.id !== id)
    delete taskInfos.value[id]
    total.value -= 1
  }

  async function updateTemplating (id: string, data: Partial<TemplatingModel>): Promise<TemplatingModel> {
    const { data: updated } = await http.patch<TemplatingModel>(`/v1/templatings/${id}`, data)
    const idx = templatings.value.findIndex((t: TemplatingModel) => t.id === id)
    if (idx !== -1) templatings.value[idx] = updated
    return updated
  }

  return { templatings, total, isLoading, error, taskInfos, uploadTemplating, fetchTemplatings, fetchTaskInfo, fetchAllTaskInfos, deleteTemplating, updateTemplating }
})
