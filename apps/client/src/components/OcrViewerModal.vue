<script setup lang="ts">
import type { components } from '@/api/types/api.schema'
import OcrViewer from '@/components/OcrViewer.vue'
import type { PageLabel } from '@/interfaces/classification'

type Page = components['schemas']['Page']

defineProps<{
  data: {
    id?: string
    pages: Page[]
  }
  predefinedLabels?: PageLabel[]
}>()

const emit = defineEmits<{ close: [] }>()
</script>

<template>
  <Teleport to="body">
    <dialog
      class="fixed inset-0 z-50 flex flex-col bg-white overflow-hidden w-full h-full max-w-full max-h-full m-0 p-0 border-0"
      open
      aria-label="Résultats OCR"
    >
      <!-- Header de la modal -->
      <div class="flex items-center justify-between px-6 py-3 border-b border-slate-200 bg-white shrink-0">
        <div class="flex items-center gap-2">
          <span class="fr-icon-file-text-line text-blue-600" aria-hidden="true" />
          <h2 class="text-base font-semibold text-slate-800">
            Résultats de l'extraction OCR
          </h2>
        </div>
        <button
          class="flex items-center justify-center w-8 h-8 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-700 transition-colors"
          aria-label="Fermer"
          @click="emit('close')"
        >
          <span class="fr-icon-close-line" aria-hidden="true" />
        </button>
      </div>

      <!-- Contenu scrollable -->
      <div class="flex-1 overflow-y-auto px-6 py-4">
        <OcrViewer
          :data="data"
          :predefined-labels="predefinedLabels"
        />
      </div>
    </dialog>
  </Teleport>
</template>
