<script setup lang="ts">
import type { components } from '@/api/types/api.schema'
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import useToaster from '@/composables/use-toaster'
import BboxDetailPanel from '@/components/BboxDetailPanel.vue'
import BboxModal from '@/components/BboxModal.vue'
import OcrImageViewer from '@/components/OcrImageViewer.vue'
import OcrMetricsModal from '@/components/OcrMetricsModal.vue'
import OcrSearchPanel from '@/components/OcrSearchPanel.vue'
import OcrViewModeToggle from '@/components/OcrViewModeToggle.vue'
import OcrChatbot from '@/components/OcrChatbot.vue'
import OcrTutorial from '@/components/OcrTutorial.vue'
import PageClassificationPanel from '@/components/PageClassificationPanel.vue'
import { useOcrReview } from '@/composables/use-ocr-review'
import { useOcrViewer } from '@/composables/use-ocr-viewer'
import type { EntityPrediction } from '@/composables/use-ocr-viewer'
import { useOcrChatbot } from '@/composables/use-ocr-chatbot'
import type { ChatSource } from '@/composables/use-ocr-chatbot'
import type { PageLabel } from '@/interfaces/classification'
import type { BboxReview, ValidationState } from '@/interfaces/review'
import { useOcrStore } from '@/stores/ocr'
import { useAnnotationsStore } from '@/stores/annotations'
import type { PageAnnotation } from '@/stores/annotations'

type ClassificationAnnotation = components['schemas']['ClassificationAnnotation']
type Layout = components['schemas']['Layout']

// Re-export for consumers that import types from this component
export type { ValidationState, BboxReview }

type Page = components['schemas']['Page']
type Bbox = components['schemas']['Bbox']

const props = defineProps<{
  data: {
    id?: string
    pages: Page[]
  }
  contentHash?: string
  predefinedLabels?: PageLabel[]
}>()

const store = useOcrStore()
const annotationsStore = useAnnotationsStore()
const { addErrorMessage, addSuccessMessage } = useToaster()
const pages = props.data.pages
const currentPage = ref(0)

const imageUrl = computed(() => pages[currentPage.value].page_url ?? undefined)
const boxes = computed<Bbox[]>(() => pages[currentPage.value]?.boxes || [])
const layouts = computed<Layout[]>(() => (pages[currentPage.value]?.layouts ?? []) as Layout[])
const hasLayouts = computed(() => pages.some((p: Page) => p.layouts && p.layouts.length > 0))
const entities = computed<EntityPrediction[]>(() => (pages[currentPage.value]?.entities ?? []) as EntityPrediction[])

const showImage = ref(true)
const drawingMode = ref(false)

const {
  corrections, drawnBoxes, pageDrawnBoxes,
  selectedBoxIdx, selectedBox, allBoxes, boxMeta, reviewedCount,
  currentPageLabels, currentPageConsent, pageConsents, pageClassifications,
  savedStateFor, isBoxHidden, toggleBoxVisibility,
  selectBox, onSave, onBoxDrawn, deleteDrawnBox,
  setPageLabels, setPageConsent, loadAnnotations, resetPage,
} = useOcrReview(() => boxes.value, () => currentPage.value)

const {
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
} = useOcrViewer(
  pages,
  currentPage,
  () => allBoxes.value,
  () => entities.value,
)

watch(currentPage, resetPage)

const totalBoxes = computed(() =>
  pages.reduce((acc: number, p: Page) => acc + (p.boxes?.length ?? 0), 0),
)

// Load existing annotations from API on mount
onMounted(async () => {
  if (!props.contentHash) return
  const existing = await annotationsStore.fetchByHash(props.contentHash)
  if (existing) loadAnnotations(existing)
})

// Metrics
const showMetrics = ref(false)

// Chatbot
const { messages: chatMessages, isLoading: chatLoading, sendMessage } = useOcrChatbot(
  () => pages,
  () => props.contentHash,
  () => props.data.id,
)

// Boxes highlighted by the chatbot (yellow) — keyed to current page
const chatHighlightedBoxes = ref<Set<number>>(new Set())

async function jumpToSource (source: ChatSource) {
  // Navigate to the first page of the source
  currentPage.value = source.pageIdx
  await nextTick()
  // Highlight all bbox indices on that page
  chatHighlightedBoxes.value = new Set(source.boxIndices)
  // Clear highlight after animation (3 × 1.5s)
  setTimeout(() => { chatHighlightedBoxes.value = new Set() }, 5000)
}

async function onDownloadText () {
  if (!props.data.id) return
  try {
    await store.downloadText(props.data.id)
    addSuccessMessage({ title: 'Succès !', description: 'Document téléchargé.' })
  }
  catch (error) {
    addErrorMessage({ title: 'Erreur :', description: `${error}` })
  }
}

const hasAnnotations = computed(() =>
  corrections.value.size > 0
  || pageDrawnBoxes.value.size > 0
  || pageClassifications.value.size > 0
  || pageConsents.value.size > 0,
)

const isSubmitting = ref(false)
const showTutorial = ref(false)

function buildAnnotationOutput (): PageAnnotation[] {
  const pagesMap = new Map<number, PageAnnotation>()

  // Helper to ensure a page entry exists
  function ensurePage (pageIdx: number) {
    if (!pagesMap.has(pageIdx)) {
      const consent = pageConsents.value.get(pageIdx)
      const labels = pageClassifications.value.get(pageIdx) ?? []
      const classifications: ClassificationAnnotation[] = labels.map(l => ({ label: l.key, description: l.definition }))
      pagesMap.set(pageIdx, {
        page: pageIdx,
        boxes: [],
        classifications,
        private: pageConsents.value.get(pageIdx) === false,
      })
    }
  }

  // Box corrections (existing boxes)
  for (const [key, review] of corrections.value) {
    const [pageIdxStr, boxIdxStr] = key.split('-')
    const pageIdx = parseInt(pageIdxStr)
    const boxIdx = parseInt(boxIdxStr)
    const page = pages[pageIdx]
    if (!page) continue
    const box = page.boxes?.[boxIdx]
    if (!box) continue

    ensurePage(pageIdx)
    pagesMap.get(pageIdx)!.boxes.push({
      index: boxIdx,
      x: box.x,
      y: box.y,
      width: box.width,
      height: box.height,
      text: review.correctedText ?? box.text ?? undefined,
      validation: review.validation ?? undefined,
      private: review.isPrivate ?? false,
    })
  }

  // Drawn (free) boxes — index is null, stored per page
  for (const [pageIdx, drawn] of pageDrawnBoxes.value) {
    for (let di = 0; di < drawn.length; di++) {
      const box = drawn[di]
      const drawnKey = `drawn-${pageIdx}-${di}`
      const review = corrections.value.get(drawnKey)
      ensurePage(pageIdx)
      pagesMap.get(pageIdx)!.boxes.push({
        index: null as any, // free annotation — no original bbox
        x: box.x,
        y: box.y,
        width: box.width,
        height: box.height,
        text: review?.correctedText ?? box.text ?? undefined,
        validation: review?.validation ?? undefined,
        private: review?.isPrivate ?? false,
      })
    }
  }

  // Pages with only classifications or consent (no box edits)
  const allPageIdxs = new Set([
    ...Array.from(pageConsents.value.keys()),
    ...Array.from(pageClassifications.value.keys()),
  ])
  for (const pageIdx of allPageIdxs) {
    ensurePage(pageIdx)
  }

  return Array.from(pagesMap.values())
}

async function submitAnnotations () {
  if (!props.contentHash) {
    addErrorMessage({ title: 'Erreur', description: 'Aucun identifiant de fichier disponible pour sauvegarder les annotations.' })
    return
  }
  isSubmitting.value = true
  try {
    const output = buildAnnotationOutput()
    await annotationsStore.upsert(props.contentHash, {
      user_id: '', // overridden server-side from token
      output,
    })
  }
  finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="w-full max-w-6xl mx-auto">
    <!-- Toolbar -->
    <div data-tour="toolbar" class="my-6 flex flex-wrap items-center justify-center gap-2 rounded-2xl border border-slate-100 bg-white px-4 py-3 shadow-sm">
      <!-- Image toggle -->
      <button
        data-tour="toggle-image"
        class="hidden md:inline-flex items-center gap-1.5 rounded-xl px-3 py-2 text-sm font-medium transition-colors"
        :class="showImage
          ? 'bg-slate-100 text-slate-700 hover:bg-slate-200'
          : 'bg-blue-50 text-blue-700 hover:bg-blue-100'"
        @click="showImage = !showImage"
      >
        <span
          :class="showImage ? 'fr-icon-eye-off-line' : 'fr-icon-eye-line'"
          style="font-size: 14px;"
          aria-hidden="true"
        />
        {{ showImage ? "Masquer l'image" : "Afficher l'image" }}
      </button>

      <span class="hidden md:block w-px h-5 bg-slate-200" />

      <!-- Annotation mode -->
      <button
        data-tour="drawing-mode"
        class="hidden md:inline-flex items-center gap-1.5 rounded-xl px-3 py-2 text-sm font-medium transition-colors"
        :class="drawingMode
          ? 'bg-violet-100 text-violet-700 ring-1 ring-violet-300 hover:bg-violet-200'
          : 'bg-slate-100 text-slate-700 hover:bg-slate-200'"
        @click="drawingMode = !drawingMode"
      >
        <span
          :class="drawingMode ? 'fr-icon-close-circle-line' : 'fr-icon-edit-line'"
          style="font-size: 14px;"
          aria-hidden="true"
        />
        {{ drawingMode ? `Arrêter l'annotation` : `Annoter une zone` }}
      </button>

      <span class="hidden md:block w-px h-5 bg-slate-200" />


      <button
        data-tour="metrics"
        class="inline-flex items-center gap-1.5 rounded-xl bg-slate-100 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-200 transition-colors"
        @click="showMetrics = true"
      >
        <span class="fr-icon-bar-chart-box-line" style="font-size: 14px;" aria-hidden="true" />
        Métriques
      </button>

      <!-- Slot pour actions supplémentaires (ex: voir le texte) -->
      <slot name="extra-actions" />

      <!-- Aide / tutoriel -->
      <button
        class="inline-flex items-center gap-1.5 rounded-xl bg-slate-100 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-200 transition-colors"
        title="Aide — découvrir les fonctionnalités"
        @click="showTutorial = true"
      >
        <span class="fr-icon-question-fill" style="font-size: 14px;" aria-hidden="true" />
        Aide
      </button>

      <!-- Télécharger -->
      <button
        class="inline-flex items-center gap-1.5 rounded-xl bg-slate-100 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-200 transition-colors"
        @click="onDownloadText"
      >
        <span class="fr-icon-download-line" style="font-size: 14px;" aria-hidden="true" />
        Télécharger
      </button>
    </div>

    <div class="md:flex gap-4 items-start hidden">
      <!-- Image + Boxes -->
      <div class="flex-1">
        <!-- Navigation de page au-dessus de l'image -->
        <div
          v-if="pages.length > 1"
          data-tour="pagination"
          class="mb-3 flex items-center justify-between rounded-2xl border border-slate-100 bg-white px-3 py-2 shadow-sm"
        >
          <button
            class="fr-btn fr-btn--tertiary-no-outline fr-btn--sm fr-icon-arrow-left-s-line"
            type="button"
            aria-label="Page précédente"
            :disabled="currentPage === 0"
            @click="currentPage > 0 && currentPage--"
          />
          <span class="text-sm text-slate-600 font-medium tabular-nums">
            Page {{ currentPage + 1 }} / {{ pages.length }}
          </span>
          <button
            class="fr-btn fr-btn--tertiary-no-outline fr-btn--sm fr-icon-arrow-right-s-line"
            type="button"
            aria-label="Page suivante"
            :disabled="currentPage === pages.length - 1"
            @click="currentPage < pages.length - 1 && currentPage++"
          />
        </div>

        <!-- Revision bar -->
        <div data-tour="progress-bar" class="mb-4 rounded-2xl border border-slate-100 bg-white px-4 py-3 shadow-sm flex items-center gap-4">
          <div class="flex-1 rounded-full overflow-hidden h-1.5 bg-slate-100">
            <div
              class="h-full rounded-full bg-emerald-500 transition-all duration-500"
              :style="{ width: totalBoxes ? `${(reviewedCount / totalBoxes) * 100}%` : '0%' }"
            />
          </div>
          <div class="flex items-center gap-3 text-xs shrink-0">
            <span class="text-slate-400">{{ totalBoxes }} zones</span>
            <span class="text-slate-300">/</span>
            <span class="font-semibold text-emerald-600">{{ reviewedCount }} révisées</span>
            <span class="inline-flex items-center rounded-full bg-emerald-50 px-2 py-0.5 font-bold text-emerald-700 tabular-nums">
              {{ totalBoxes ? Math.round((reviewedCount / totalBoxes) * 100) : 0 }} %
            </span>
          </div>
        </div>

        <OcrImageViewer
          data-tour="image-viewer"
          :all-boxes="allBoxes"
          :box-meta="boxMeta"
          :show-image="showImage"
          :drawing-mode="drawingMode"
          :selected-box-idx="selectedBoxIdx"
          :image-url="imageUrl"
          :highlighted-box-indices="isSearchActive ? searchMatchIndices : chatHighlightedBoxes"
          :dimmed-when-search="isSearchActive"
          :view-mode="viewMode"
          :layout-boxes="layouts"
          :entity-boxes="entities"
          :entity-search-match-indices="isEntitySearchActive ? entitySearchMatchIndices : undefined"
          @select="selectBox"
          @toggle-visibility="toggleBoxVisibility"
          @drawn="onBoxDrawn"
        />
      </div>

      <!-- Right sidebar : classification toujours visible -->
      <div data-tour="sidebar" class="w-72 shrink-0 sticky top-4 flex flex-col gap-3">
        <!-- Toggle OCR / Layout / Entités -->
        <OcrViewModeToggle data-tour="view-mode-toggle" v-model="viewMode" />

        <!-- Barre de recherche OCR -->
        <OcrSearchPanel
          v-if="viewMode === 'ocr'"
          v-model="searchQuery"
          placeholder="Rechercher dans le texte…"
          :results="crossPageResults"
          :current-page="currentPage"
          accent-color="amber"
          :quote-samples="true"
          @go-to-page="goToSearchPage"
        />

        <!-- Barre de recherche Entités -->
        <OcrSearchPanel
          v-if="viewMode === 'entity'"
          v-model="entitySearchQuery"
          placeholder="Rechercher une entité…"
          :results="crossPageEntityResults"
          :current-page="currentPage"
          accent-color="rose"
          @go-to-page="currentPage = $event"
        />

        <PageClassificationPanel
          data-tour="classification"
          :model-value="currentPageLabels"
          :predefined-labels="predefinedLabels"
          :consent-for-training="currentPageConsent"
          @update:model-value="setPageLabels"
          @update:consent-for-training="(v) => { setPageConsent(v); if (contentHash) submitAnnotations() }"
          @save="submitAnnotations"
        />
      </div>
    </div>

    <!-- Modal bbox : détail de la zone sélectionnée -->
    <BboxModal
      v-if="selectedBox"
      :box="selectedBox"
      :saved-state="selectedBoxIdx !== null ? savedStateFor(selectedBoxIdx) : undefined"
      :is-hidden="selectedBoxIdx !== null ? isBoxHidden(selectedBoxIdx) : false"
      @close="selectedBoxIdx = null"
      @save="(review) => { onSave(review); if (contentHash) submitAnnotations() }"
      @delete="deleteDrawnBox"
      @toggle-visibility="selectedBoxIdx !== null && toggleBoxVisibility(selectedBoxIdx)"
    />

    <div class="my-4">
      <DsfrAlert>
        L’extraction peut comporter des erreurs, veuillez vérifier les résultats.
      </DsfrAlert>
    </div>

    <!-- Bandeau info réentraînement -->
    <div class="my-3 flex items-start gap-3 rounded-lg border border-blue-100 bg-blue-50 px-4 py-3 text-xs text-blue-700">
      <span class="fr-icon-information-line shrink-0 mt-0.5" aria-hidden="true" />
      <span>
        Vos annotations (textes corrigés, zones dessinées) peuvent contribuer à améliorer le modèle OCR.
        <strong>Les données marquées comme privées sont toujours exclues.</strong>
        Utilisez les contrôles ci-dessous pour indiquer votre consentement page par page.
      </span>
    </div>

    <!-- Metrics modal -->
    <OcrMetricsModal
      v-if="showMetrics"
      :pages="pages"
      :corrections="corrections"
      :drawn-boxes="drawnBoxes"
      :current-page="currentPage"
      @close="showMetrics = false"
    />

    <!-- Floating chatbot -->
    <OcrChatbot
      :messages="chatMessages"
      :is-loading="chatLoading"
      @send="sendMessage"
      @jump-to="jumpToSource"
    />

    <!-- Tutorial overlay -->
    <OcrTutorial
      v-if="showTutorial"
      @close="showTutorial = false"
    />
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
.slide-enter-active,
.slide-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateX(12px);
}

.drawer-enter-active,
.drawer-leave-active {
  transition: transform 0.25s ease, opacity 0.25s ease;
}
.drawer-enter-from,
.drawer-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
</style>
