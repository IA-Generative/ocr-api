import { computed, ref } from 'vue'
import type { components } from '@/api/types/api.schema'
import type { BboxReview } from '@/interfaces/review'
import type { DrawnBox } from '@/composables/use-box-drawing'
import type { PageLabel } from '@/interfaces/classification'

type Bbox = components['schemas']['Bbox']
type AnnotationModel = components['schemas']['AnnotationModel']

export interface BoxMeta {
  hidden: boolean
  reviewClass: string
  correctedText?: string
}

export function useOcrReview (
  getBoxes: () => Bbox[],
  getCurrentPage: () => number,
) {
  // drawn boxes stored per page so they survive page navigation
  const pageDrawnBoxes = ref<Map<number, DrawnBox[]>>(new Map())
  const selectedBoxIdx = ref<number | null>(null)
  const corrections = ref<Map<string, BboxReview>>(new Map())
  const hiddenBoxes = ref<Set<string>>(new Set())
  const pageClassifications = ref<Map<number, PageLabel[]>>(new Map())
  const pageConsents = ref<Map<number, boolean | null>>(new Map())

  // drawn boxes for the current page (derived)
  const drawnBoxes = computed<DrawnBox[]>(() =>
    pageDrawnBoxes.value.get(getCurrentPage()) ?? [],
  )

  const allBoxes = computed<(Bbox | DrawnBox)[]>(() => [
    ...getBoxes(),
    ...drawnBoxes.value,
  ])

  const selectedBox = computed(() =>
    selectedBoxIdx.value !== null ? allBoxes.value[selectedBoxIdx.value] ?? null : null,
  )

  const currentPageLabels = computed(() => pageClassifications.value.get(getCurrentPage()) ?? [])
  const currentPageConsent = computed(() => pageConsents.value.get(getCurrentPage()) ?? null)
  const reviewedCount = computed(() => corrections.value.size)

  const boxMeta = computed<BoxMeta[]>(() =>
    allBoxes.value.map((_: Bbox | DrawnBox, idx: number) => ({
      hidden: isBoxHidden(idx),
      reviewClass: reviewClassFor(idx),
      correctedText: savedStateFor(idx)?.correctedText,
    })),
  )

  function correctionKey (pageIdx: number, boxIdx: number) {
    return `${pageIdx}-${boxIdx}`
  }

  function savedStateFor (boxIdx: number): BboxReview | undefined {
    const page = getCurrentPage()
    const originalCount = getBoxes().length
    if (boxIdx >= originalCount) {
      // drawn box
      const drawnIdx = boxIdx - originalCount
      return corrections.value.get(`drawn-${page}-${drawnIdx}`)
    }
    return corrections.value.get(correctionKey(page, boxIdx))
  }

  function isBoxHidden (boxIdx: number): boolean {
    return hiddenBoxes.value.has(correctionKey(getCurrentPage(), boxIdx))
  }

  function toggleBoxVisibility (boxIdx: number) {
    const key = correctionKey(getCurrentPage(), boxIdx)
    const next = new Set(hiddenBoxes.value)
    next.has(key) ? next.delete(key) : next.add(key)
    hiddenBoxes.value = next
  }

  function selectBox (idx: number) {
    selectedBoxIdx.value = selectedBoxIdx.value === idx ? null : idx
  }

  function onSave (review: BboxReview) {
    if (selectedBoxIdx.value === null) return
    const page = getCurrentPage()
    const originalCount = getBoxes().length
    const key = selectedBoxIdx.value >= originalCount
      ? `drawn-${page}-${selectedBoxIdx.value - originalCount}`
      : correctionKey(page, selectedBoxIdx.value)
    corrections.value = new Map(corrections.value).set(key, review)
  }

  function onBoxDrawn (box: DrawnBox) {
    const page = getCurrentPage()
    const current = pageDrawnBoxes.value.get(page) ?? []
    const updated = new Map(pageDrawnBoxes.value).set(page, [...current, box])
    pageDrawnBoxes.value = updated
    selectedBoxIdx.value = getBoxes().length + (updated.get(page)!.length - 1)
  }

  function deleteDrawnBox () {
    if (selectedBoxIdx.value === null) return
    const drawnIdx = selectedBoxIdx.value - getBoxes().length
    if (drawnIdx < 0) return
    const page = getCurrentPage()
    const current = pageDrawnBoxes.value.get(page) ?? []
    const updated = new Map(pageDrawnBoxes.value).set(page, current.filter((_, i) => i !== drawnIdx))
    pageDrawnBoxes.value = updated
    selectedBoxIdx.value = null
  }

  function reviewClassFor (boxIdx: number): string {
    if (boxIdx >= getBoxes().length) return 'box-drawn'
    const review = savedStateFor(boxIdx)
    if (!review) return ''
    if (review.validation === 'valid') return 'box-reviewed-valid'
    if (review.validation === 'invalid') return 'box-reviewed-invalid'
    return 'box-reviewed-corrected'
  }

  function setPageLabels (labels: PageLabel[]) {
    pageClassifications.value = new Map(pageClassifications.value).set(getCurrentPage(), labels)
  }

  function setPageConsent (value: boolean | null) {
    pageConsents.value = new Map(pageConsents.value).set(getCurrentPage(), value)
  }

  function loadAnnotations (annotation: AnnotationModel) {
    const newCorrections = new Map<string, BboxReview>()
    const newClassifications = new Map<number, PageLabel[]>()
    const newConsents = new Map<number, boolean | null>()
    const newDrawnBoxes = new Map<number, DrawnBox[]>()

    for (const page of annotation.output ?? []) {
      const pageIdx = page.page

      if (page.private) {
        newConsents.set(pageIdx, false)
      }
      // page.private === false means either not set or explicitly shared — leave consent as null (neutral)

      if (page.classifications && page.classifications.length > 0) {
        // Preserve existing readonly (auto-predicted) labels for this page
        const existingReadonly = (pageClassifications.value.get(pageIdx) ?? []).filter(l => l.readonly)
        const annotationLabels: PageLabel[] = page.classifications.map(c => ({
          key: c.label,
          definition: c.description ?? '',
          predefined: false,
        }))
        // Merge: readonly first, then annotation labels not already present
        const readonlyKeys = new Set(existingReadonly.map(l => l.key))
        const merged = [
          ...existingReadonly,
          ...annotationLabels.filter(l => !readonlyKeys.has(l.key)),
        ]
        newClassifications.set(pageIdx, merged)
      }

      // Separate original-bbox corrections from free drawn boxes (index === null)
      const drawnForPage: DrawnBox[] = []
      // We need to know how many original boxes exist for the page to assign drawn keys.
      // We don't have that info here, so drawn boxes get keys after corrections by insertion order.
      let drawnOffset = 0

      for (const box of page.boxes ?? []) {
        if (box.index === null || box.index === undefined) {
          // Free drawn box — restore as DrawnBox
          drawnForPage.push({
            isDrawn: true,
            x: box.x,
            y: box.y,
            width: box.width,
            height: box.height,
            text: box.text ?? '',
            confidence: 1,
          } as DrawnBox)
          // Correction key will be resolved in OcrViewer using originalBoxCount + drawnOffset
          // Store in corrections too so BboxDetailPanel can load metadata
          // Key format for drawn: we use a sentinel prefix 'drawn-{page}-{drawnOffset}'
          const key = `drawn-${pageIdx}-${drawnOffset}`
          newCorrections.set(key, {
            correctedText: box.text ?? '',
            validation: (box.validation as 'valid' | 'invalid' | null) ?? null,
            isPrivate: box.private ?? false,
          })
          drawnOffset++
        }
        else {
          const key = `${pageIdx}-${box.index}`
          newCorrections.set(key, {
            correctedText: box.text ?? '',
            validation: (box.validation as 'valid' | 'invalid' | null) ?? null,
            isPrivate: box.private ?? false,
          })
        }
      }

      if (drawnForPage.length > 0) {
        newDrawnBoxes.set(pageIdx, drawnForPage)
      }
    }

    corrections.value = newCorrections
    // Merge: keep readonly labels from pages not covered by annotations
    for (const [pageIdx, labels] of pageClassifications.value) {
      const readonlyLabels = labels.filter(l => l.readonly)
      if (readonlyLabels.length > 0 && !newClassifications.has(pageIdx)) {
        newClassifications.set(pageIdx, readonlyLabels)
      }
    }
    pageClassifications.value = newClassifications
    pageConsents.value = newConsents
    pageDrawnBoxes.value = newDrawnBoxes
  }

  function resetPage () {
    selectedBoxIdx.value = null
  }

  return {
    corrections,
    drawnBoxes,
    pageDrawnBoxes,
    selectedBoxIdx,
    selectedBox,
    allBoxes,
    boxMeta,
    reviewedCount,
    currentPageLabels,
    currentPageConsent,
    pageConsents,
    pageClassifications,
    savedStateFor,
    isBoxHidden,
    toggleBoxVisibility,
    selectBox,
    onSave,
    onBoxDrawn,
    deleteDrawnBox,
    setPageLabels,
    setPageConsent,
    loadAnnotations,
    resetPage,
  }
}
