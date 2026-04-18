import { computed, ref, type Ref } from 'vue'
import type { components } from '@/api/types/api.schema'
import type { DrawnBox } from '@/composables/use-box-drawing'

type Bbox = components['schemas']['Bbox']
type Page = components['schemas']['Page']

export type EntityPrediction = {
  entity_name: string
  confidence: number
  value?: string | null
  bbox?: Bbox[] | null
  pages?: number[] | null
}

export type PageSearchResult = { pageIdx: number; count: number; samples: string[] }
export type PageEntitySearchResult = { pageIdx: number; count: number; samples: string[] }

export function useOcrViewer(
  pages: Page[],
  currentPage: Ref<number>,
  getAllBoxes: () => (Bbox | DrawnBox)[],
  getEntities: () => EntityPrediction[],
  allEntities?: EntityPrediction[],
) {
  const viewMode = ref<'ocr' | 'layout' | 'entity'>('ocr')

  // ── OCR search ────────────────────────────────────────────────────────
  const searchQuery = ref('')

  const searchMatchIndices = computed<Set<number>>(() => {
    const q = searchQuery.value.trim().toLowerCase()
    if (!q) return new Set<number>()
    const matched = new Set<number>()
    getAllBoxes().forEach((box, idx) => {
      if (((box as Bbox).text ?? '').toLowerCase().includes(q)) matched.add(idx)
    })
    return matched
  })

  const isSearchActive = computed(() => searchQuery.value.trim().length > 0)

  const crossPageResults = computed<PageSearchResult[]>(() => {
    const q = searchQuery.value.trim().toLowerCase()
    if (!q) return []
    return pages
      .map((page, pageIdx) => {
        const matching = (page.boxes ?? []).filter(b => (b.text ?? '').toLowerCase().includes(q))
        return {
          pageIdx,
          count: matching.length,
          samples: matching.slice(0, 3).map(b => b.text ?? ''),
        }
      })
      .filter(r => r.count > 0)
  })

  function goToSearchPage(pageIdx: number) {
    currentPage.value = pageIdx
  }

  // ── Entity search ─────────────────────────────────────────────────────
  const entitySearchQuery = ref('')

  const entitySearchMatchIndices = computed<Set<number>>(() => {
    const q = entitySearchQuery.value.trim().toLowerCase()
    if (!q) return new Set<number>()
    const matched = new Set<number>()
    getEntities().forEach((e, idx) => {
      const hay = `${e.entity_name} ${e.value ?? ''}`.toLowerCase()
      if (hay.includes(q)) matched.add(idx)
    })
    return matched
  })

  const isEntitySearchActive = computed(() => entitySearchQuery.value.trim().length > 0)

  const crossPageEntityResults = computed<PageEntitySearchResult[]>(() => {
    const q = entitySearchQuery.value.trim().toLowerCase()
    if (!q) return []

    // Si les entités sont au niveau racine (avec champ pages), les regrouper par page
    if (allEntities && allEntities.length > 0) {
      const byPage = new Map<number, EntityPrediction[]>()
      for (const e of allEntities) {
        const hay = `${e.entity_name} ${e.value ?? ''}`.toLowerCase()
        if (!hay.includes(q)) continue
        const entityPages = e.pages?.length ? e.pages : [0]
        for (const p of entityPages) {
          if (!byPage.has(p)) byPage.set(p, [])
          byPage.get(p)!.push(e)
        }
      }
      return Array.from(byPage.entries())
        .sort(([a], [b]) => a - b)
        .map(([pageIdx, matched]) => ({
          pageIdx,
          count: matched.length,
          samples: matched
            .slice(0, 3)
            .map((e: EntityPrediction) => `${e.entity_name}${e.value ? ` : ${e.value}` : ''}`),
        }))
    }

    // Fallback : entités au niveau page (legacy)
    return pages
      .map((page, pageIdx) => {
        const matching = ((page as any).entities ?? [] as EntityPrediction[]).filter(
          (e: EntityPrediction) => `${e.entity_name} ${e.value ?? ''}`.toLowerCase().includes(q),
        )
        return {
          pageIdx,
          count: matching.length,
          samples: matching
            .slice(0, 3)
            .map((e: EntityPrediction) => `${e.entity_name}${e.value ? ` : ${e.value}` : ''}`),
        }
      })
      .filter(r => r.count > 0)
  })

  return {
    viewMode,
    searchQuery,
    searchMatchIndices,
    isSearchActive,
    crossPageResults,
    goToSearchPage,
    entitySearchQuery,
    entitySearchMatchIndices,
    isEntitySearchActive,
    crossPageEntityResults,
  }
}
