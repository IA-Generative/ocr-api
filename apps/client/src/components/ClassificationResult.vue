<template>
  <div class="flex flex-col gap-4">

    <!-- En-tête avec pagination -->
    <div class="flex items-center justify-between">
      <h3 class="fr-h5 mb-0">Résultats de classification</h3>

      <div v-if="pages.length > 1" class="flex items-center gap-2">
        <button
          class="fr-btn fr-btn--tertiary-no-outline fr-btn--sm fr-icon-arrow-left-s-line"
          type="button"
          :disabled="currentIndex === 0"
          aria-label="Page précédente"
          @click="currentIndex--"
        />
        <span class="text-sm text-[var(--text-mention-grey)]">
          Page {{ currentPage.page + 1 }} / {{ pages.length }}
        </span>
        <button
          class="fr-btn fr-btn--tertiary-no-outline fr-btn--sm fr-icon-arrow-right-s-line"
          type="button"
          :disabled="currentIndex === pages.length - 1"
          aria-label="Page suivante"
          @click="currentIndex++"
        />
      </div>
    </div>

    <!-- Contenu : vignette + scores -->
    <div class="flex gap-5 items-start">

      <!-- Vignette de la page -->
      <div class="shrink-0 w-28">
        <img
          v-if="currentPage.pageUrl"
          :src="currentPage.pageUrl"
          :alt="`Aperçu page ${currentPage.page + 1}`"
          class="w-full border border-[var(--border-default-grey)] shadow-sm object-contain"
        />
        <div
          v-else
          class="w-full aspect-[3/4] border border-[var(--border-default-grey)] bg-[var(--background-contrast-grey)] flex items-center justify-center"
        >
          <span class="fr-icon-image-line text-[var(--text-mention-grey)]" aria-hidden="true" />
        </div>

        <!-- Badge top label sous l'image -->
        <div class="mt-1.5 flex justify-center">
          <span
            v-if="currentPage.topLabel"
            class="text-xs font-semibold px-2 py-0.5 rounded-full bg-[var(--background-flat-info)] text-white truncate max-w-full"
            :title="currentPage.topLabel"
          >
            {{ currentPage.topLabel }}
          </span>
          <span v-else class="text-xs text-[var(--text-mention-grey)]">—</span>
        </div>
      </div>

      <!-- Barres de score -->
      <div class="flex flex-col gap-3 flex-1">
      <div
        v-for="classif in currentPage.classifications"
        :key="classif.label.label"
        class="flex items-center gap-3"
      >
        <span
          class="text-sm w-32 shrink-0 font-medium truncate"
          :class="classif.label.label === currentPage.topLabel
            ? 'text-[var(--text-active-blue-france)]'
            : 'text-[var(--text-mention-grey)]'"
          :title="classif.label.label"
        >
          {{ classif.label.label }}
        </span>

        <div class="flex-1 h-2 rounded-full bg-[var(--background-contrast-grey)] overflow-hidden">
          <div
            class="h-full rounded-full transition-all duration-500"
            :class="classif.label.label === currentPage.topLabel
              ? 'bg-[var(--background-flat-info)]'
              : 'bg-[var(--border-default-grey)]'"
            :style="{ width: `${classif.scorePercent}%` }"
          />
        </div>

        <span class="text-xs text-[var(--text-mention-grey)] w-10 text-right shrink-0">
          {{ classif.scorePercent }}%
        </span>
      </div>
    </div>

    </div>

    <!-- Miniature de pagination -->
    <div v-if="pages.length > 1" class="flex gap-1.5 justify-center pt-1">
      <button
        v-for="(_, i) in pages"
        :key="i"
        type="button"
        class="h-1.5 rounded-full transition-all duration-200"
        :class="i === currentIndex
          ? 'w-4 bg-[var(--background-flat-info)]'
          : 'w-1.5 bg-[var(--border-default-grey)]'"
        :aria-label="`Aller à la page ${pages[i].page + 1}`"
        @click="currentIndex = i"
      />
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

export type ClassificationResult = {
  label: { label: string; definition: string }
  confidence: number
  scorePercent: number
}

export type ClassificationPage = {
  page: number
  pageUrl: string | null
  topLabel: string | null
  classifications: ClassificationResult[]
}

const props = defineProps<{
  pages: ClassificationPage[]
}>()

const currentIndex = ref(0)
const currentPage = computed(() => props.pages[currentIndex.value])

import { computed } from 'vue'
</script>
