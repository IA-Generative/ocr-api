<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useOcrStore } from '@/stores/ocr'
import useToaster from '@/composables/use-toaster'
import type { Bbox, Page } from '@/api/types'
import type { CSSProperties } from 'vue'

const props = defineProps<{
  data: {
    id?: string
    pages: Page[]
  }
}>()

const store = useOcrStore()
const { addErrorMessage, addSuccessMessage } = useToaster()
const pages = props.data.pages
const currentPage = ref(0)

// Paginatination pages
const paginationPages = computed(() =>
  pages.map((p, idx) => ({
    href: p.page_url,
    label: String(idx + 1),
    title: `Page ${idx + 1}`,
  })),
)

const imageUrl = computed(() => pages[currentPage.value].page_url)
const boxes = computed<Bbox[]>(() => {
  return pages[currentPage.value]?.boxes || []
})
const showImage = ref(true)

const imgRef = ref<HTMLImageElement | null>(null)
const imgDimensions = ref({ width: 0, height: 0 })
let resizeObserver: ResizeObserver

function styleForBox(box: Bbox): CSSProperties {
  const W = imgDimensions.value.width
  const H = imgDimensions.value.height
  return {
    position: 'absolute',
    left: `${box.x * W}px`,
    top: `${box.y * H}px`,
    height: `${box.height * H}px`,
    width: `${box.width * W}px`,
    zIndex: 20,
    whiteSpace: 'nowrap',
  }
}

onMounted(() => {
  if (!imgRef.value) return
  imgDimensions.value = {
    width: imgRef.value.clientWidth,
    height: imgRef.value.clientHeight,
  }
  resizeObserver = new ResizeObserver((entries) => {
    for (const { contentRect } of entries) {
      imgDimensions.value = {
        width: contentRect.width,
        height: contentRect.height,
      }
    }
  })
  resizeObserver.observe(imgRef.value)
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
})

function copyText(text: string) {
  navigator.clipboard.writeText(text).then(() => {
    addSuccessMessage({
      title: 'Texte copié :',
      description: `${text}`,
    })
  }).catch((error) => {
    addErrorMessage({
      title: 'Erreur lors de la copie :',
      description: `${error}`,
    })
  })
}

/**
 * Handler du bouton Télécharger
 */
async function onDownloadText() {
  if (!props.data.id) return
  try {
    await store.downloadText(props.data.id)
    addSuccessMessage({
      title: 'Succès !',
      description: `Document téléchargé.`,
    })
  } catch (error) {
    addErrorMessage({
      title: 'Erreur :',
      description: `${error}`,
    })
  }
}
</script>

<template>
  <div class="w-full max-w-4xl mx-auto">
    <!-- Toggle Button -->
    <div class="my-8 flex gap-4">
      <div class="hidden md:block">
        <DsfrButton
          size="lg"
          :label="showImage ? 'Masquer l’image' : 'Afficher l’image'"
          secondary
          @click="showImage = !showImage"
        />
      </div>
      <div>
        <DsfrButton
          size="lg"
          label="Télécharger"
          secondary
          @click="onDownloadText"
        />
      </div>
    </div>

    <div class="relative w-full border-1 border-slate-300 hidden md:block">
      <!-- Image with dynamic opacity -->
      <img
        ref="imgRef"
        :src="imageUrl"
        alt="OCR page"
        class="block w-full h-auto transition-opacity duration-300" :class="[showImage ? 'opacity-100' : 'opacity-0']"
      >

      <!-- Bounding Boxes -->
      <div
        v-for="(box, idx) in boxes"
        :key="idx"
        :style="styleForBox(box)"
        :class="showImage
          ? 'box-visible pointer-events-auto'
          : 'box-hidden pointer-events-auto'"
      >
        <span v-if="!showImage" class="text-xs font-bold text-black">
          {{ box.text }}
        </span>
        <!-- Affiche taille + bouton copier -->
        <div class="relative bg-opacity-75 h-full">
          <button
            class="absolute top-[-10px] left-[-25px] z-100"
            @click.stop="copyText(box.text)"
          >
            <span class="fr-icon-draft-line" aria-hidden="true" />
          </button>
        </div>
      </div>
    </div>

    <div class="my-4">
      <DsfrAlert>
        L’extraction peut comporter des erreurs, veuillez vérifier les résultats.
      </DsfrAlert>
    </div>

    <!-- DSFR Pagination Controls (hidden on mobile/tablet) -->
    <div class="mt-4 hidden md:flex justify-center">
      <DsfrPagination
        v-model:current-page="currentPage"
        :pages="paginationPages"
        :trunc-limit="5"
      />
    </div>
  </div>
</template>

<style scoped>
.box-visible {
  position: absolute;
  background-color: rgba(255, 0, 0, 0.3);
  border: 1px solid rgba(255, 0, 0, 0.8);
}
.box-hidden {
  position: absolute;
  background-color: transparent;
  border: none;
}
</style>
