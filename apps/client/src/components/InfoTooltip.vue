<script setup lang="ts">
import { ref } from 'vue'

defineProps<{ text: string }>()

const show = ref(false)
const btnRef = ref<HTMLButtonElement | null>(null)
const tipRef = ref<HTMLDivElement | null>(null)
</script>

<template>
  <div class="relative inline-flex items-center">
    <button
      ref="btnRef"
      type="button"
      class="flex items-center justify-center w-4 h-4 rounded-full bg-slate-200 text-slate-500 hover:bg-blue-100 hover:text-blue-600 transition-colors text-[10px] font-bold leading-none"
      aria-label="Information"
      @mouseenter="show = true"
      @mouseleave="show = false"
      @focus="show = true"
      @blur="show = false"
    >
      i
    </button>

    <Transition name="tip">
      <div
        v-if="show"
        ref="tipRef"
        role="tooltip"
        class="absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2 w-56 rounded-xl bg-slate-800 text-white text-xs leading-relaxed px-3 py-2 shadow-xl pointer-events-none"
      >
        {{ text }}
        <!-- Arrow -->
        <div class="absolute top-full left-1/2 -translate-x-1/2 w-0 h-0 border-x-4 border-x-transparent border-t-4 border-t-slate-800" />
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.tip-enter-active, .tip-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.tip-enter-from, .tip-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(4px);
}
</style>
