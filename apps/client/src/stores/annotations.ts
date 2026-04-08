import type { components } from '@/api/types/api.schema'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import createHttpClient from '@/api/http-client'
import { OCR_API_URL } from '@/utils/constants'
import useToaster from '@/composables/use-toaster'

// ---------------------------------------------------------------------------
// Types from generated OpenAPI schema
// ---------------------------------------------------------------------------

type AnnotationModel = components['schemas']['AnnotationModel']
type AnnotationStats = components['schemas']['AnnotationStats']
type AnnotationUpsertForm = components['schemas']['AnnotationUpsertForm']
type PageAnnotation = components['schemas']['PageAnnotation']
type Pagination = components['schemas']['Pagination_AnnotationModel_']

export type { AnnotationModel, AnnotationStats, AnnotationUpsertForm, PageAnnotation }

// ---------------------------------------------------------------------------
// Store
// ---------------------------------------------------------------------------

const http = createHttpClient(OCR_API_URL)
const { addErrorMessage, addSuccessMessage } = useToaster()

export const useAnnotationsStore = defineStore('annotations', () => {
  const current = ref<AnnotationModel | null>(null)
  const userAnnotations = ref<Pagination>({ items: [], page: 1, page_size: 20, total: 0 })
  const stats = ref<AnnotationStats | null>(null)
  const loading = ref(false)

  // ------------------------------------------------------------------
  // Fetch by file hash
  // ------------------------------------------------------------------
  async function fetchByHash(contentHash: string): Promise<AnnotationModel | null> {
    loading.value = true
    try {
      const { data } = await http.get<AnnotationModel>(`/annotations/${encodeURIComponent(contentHash)}`)
      current.value = data
      return data
    }
    catch (err: any) {
      if (err?.response?.status !== 404) {
        addErrorMessage({ title: 'Erreur', description: `Impossible de charger l'annotation : ${err?.message ?? err}` })
      }
      current.value = null
      return null
    }
    finally {
      loading.value = false
    }
  }

  // ------------------------------------------------------------------
  // Fetch paginated list for the current user
  // ------------------------------------------------------------------
  async function fetchUserAnnotations(page = 1, page_size = 20): Promise<void> {
    loading.value = true
    try {
      const { data } = await http.get<Pagination>('/annotations/user/', { params: { page, page_size } })
      userAnnotations.value = {
        items: data.items ?? [],
        page: data.page ?? page,
        page_size: data.page_size ?? page_size,
        total: data.total ?? 0,
      }
    }
    catch (err: any) {
      addErrorMessage({ title: 'Erreur', description: `Impossible de charger les annotations : ${err?.message ?? err}` })
    }
    finally {
      loading.value = false
    }
  }

  // ------------------------------------------------------------------
  // Upsert (create or update)
  // ------------------------------------------------------------------
  async function upsert(contentHash: string, form: AnnotationUpsertForm): Promise<AnnotationModel | null> {
    loading.value = true
    try {
      const { data } = await http.put<AnnotationModel>(`/annotations/${encodeURIComponent(contentHash)}`, form)
      current.value = data
      // Update local list if present
      const idx = userAnnotations.value.items.findIndex(a => a.content_hash === contentHash)
      if (idx >= 0) userAnnotations.value.items[idx] = data
      return data
    }
    catch (err: any) {
      addErrorMessage({ title: 'Erreur', description: `Impossible de sauvegarder l'annotation : ${err?.message ?? err}` })
      return null
    }
    finally {
      loading.value = false
    }
  }

  // ------------------------------------------------------------------
  // Delete
  // ------------------------------------------------------------------
  async function deleteAnnotation(contentHash: string): Promise<void> {
    try {
      await http.delete(`/annotations/${encodeURIComponent(contentHash)}`)
      if (current.value?.content_hash === contentHash) current.value = null
      userAnnotations.value.items = userAnnotations.value.items.filter(a => a.content_hash !== contentHash)
      userAnnotations.value.total = Math.max(0, userAnnotations.value.total - 1)
      addSuccessMessage({ title: 'Supprimé', description: 'Annotation supprimée' })
    }
    catch (err: any) {
      addErrorMessage({ title: 'Erreur', description: `Impossible de supprimer l'annotation : ${err?.message ?? err}` })
      throw err
    }
  }

  // ------------------------------------------------------------------
  // Stats
  // ------------------------------------------------------------------
  async function fetchStats(): Promise<void> {
    try {
      const { data } = await http.get<AnnotationStats>('/stats/annotations')
      stats.value = data
    }
    catch (err: any) {
      addErrorMessage({ title: 'Erreur', description: `Impossible de charger les statistiques : ${err?.message ?? err}` })
    }
  }

  return {
    current,
    userAnnotations,
    stats,
    loading,
    fetchByHash,
    fetchUserAnnotations,
    upsert,
    deleteAnnotation,
    fetchStats,
  }
})
