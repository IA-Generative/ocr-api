<script setup lang="ts">
import { computed } from 'vue'
import type { PageSearchResult } from '@/composables/use-ocr-viewer'

const props = withDefaults(defineProps<{
  modelValue: string
  placeholder: string
  results: PageSearchResult[]
  currentPage: number
  accentColor?: 'amber' | 'rose'
  quoteSamples?: boolean
}>(), {
  accentColor: 'amber',
  quoteSamples: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'go-to-page': [pageIdx: number]
}>()

const isActive = computed(() => props.modelValue.trim().length > 0)

// Full class strings so Tailwind can scan them at build time
const colors = computed(() => {
  if (props.accentColor === 'rose') {
    return {
      activeRow: 'bg-rose-50 hover:bg-rose-100',
      activeLabel: 'text-rose-700',
      activeBadge: 'bg-rose-200 text-rose-800',
      currentMark: 'text-rose-400',
    }
  }
  return {
    activeRow: 'bg-amber-50 hover:bg-amber-100',
    activeLabel: 'text-amber-700',
    activeBadge: 'bg-amber-200 text-amber-800',
    currentMark: 'text-amber-500',
  }
})
</script>

<template>
  <div class="flex flex-col rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
    <!-- Search input -->
    <div class="flex items-center gap-2 px-3 py-2">
      <span class="fr-icon-search-line text-slate-400 shrink-0" style="font-size: 15px;" aria-hidden="true" />
      <input
        :value="modelValue"
        type="search"
        :placeholder="placeholder"
        class="flex-1 bg-transparent text-sm outline-none text-slate-700 placeholder:text-slate-400 min-w-0"
        @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      />
      <button
        v-if="isActive"
        class="shrink-0 text-slate-400 hover:text-slate-600 transition-colors"
        aria-label="Effacer la recherche"
        @click="emit('update:modelValue', '')"
      >
        <span class="fr-icon-close-line" style="font-size: 13px;" aria-hidden="true" />
      </button>
    </div>

    <!-- Cross-page results -->
    <transition name="slide-down">
      <div
        v-if="isActive"
        class="border-t border-slate-100 max-h-56 overflow-y-auto"
      >
        <div
          v-if="results.length === 0"
          class="px-3 py-3 text-xs text-slate-400 text-center"
        >
          Aucun résultat
        </div>
        <button
          v-for="result in results"
          :key="result.pageIdx"
          class="w-full text-left px-3 py-2.5 border-b border-slate-50 last:border-0 transition-colors"
          :class="result.pageIdx === currentPage ? colors.activeRow : 'hover:bg-slate-50'"
          @click="emit('go-to-page', result.pageIdx)"
        >
          <div class="flex items-center justify-between mb-1">
            <span
              class="text-xs font-semibold"
              :class="result.pageIdx === currentPage ? colors.activeLabel : 'text-slate-600'"
            >
              Page {{ result.pageIdx + 1 }}
              <span
                v-if="result.pageIdx === currentPage"
                class="ml-1"
                :class="colors.currentMark"
              >(actuelle)</span>
            </span>
            <span
              class="text-xs font-bold tabular-nums px-1.5 py-0.5 rounded-full"
              :class="result.pageIdx === currentPage ? colors.activeBadge : 'bg-slate-100 text-slate-600'"
            >
              {{ result.count }}
            </span>
          </div>
          <div class="flex flex-col gap-0.5">
            <span
              v-for="(sample, si) in result.samples"
              :key="si"
              class="text-xs text-slate-500 truncate"
            >
              <template v-if="quoteSamples">"{{ sample }}"</template>
              <template v-else>{{ sample }}</template>
            </span>
          </div>
        </button>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: max-height 0.2s ease, opacity 0.2s ease;
  max-height: 300px;
}
.slide-down-enter-from,
.slide-down-leave-to {
  max-height: 0;
  opacity: 0;
}
</style>
