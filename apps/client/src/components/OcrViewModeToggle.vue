<script setup lang="ts">
defineProps<{
  modelValue: 'ocr' | 'layout' | 'entity'
}>()

const emit = defineEmits<{
  'update:modelValue': [mode: 'ocr' | 'layout' | 'entity']
}>()
</script>

<template>
  <div class="flex items-center rounded-xl overflow-hidden border border-slate-200 text-sm font-medium shadow-sm">
    <button
      class="flex-1 py-2 transition-colors"
      :class="modelValue === 'ocr'
        ? 'bg-teal-500 text-white'
        : 'bg-white text-slate-600 hover:bg-slate-50'"
      @click="emit('update:modelValue', 'ocr')"
    >
      OCR
    </button>
    <button
      class="flex-1 py-2 transition-colors"
      :class="modelValue === 'layout'
        ? 'bg-violet-500 text-white'
        : 'bg-white text-slate-600 hover:bg-slate-50'"
      @click="emit('update:modelValue', 'layout')"
    >
      Layout
    </button>
    <button
      class="flex-1 py-2 transition-colors"
      :class="modelValue === 'entity'
        ? 'bg-rose-500 text-white'
        : 'bg-white text-slate-600 hover:bg-slate-50'"
      @click="emit('update:modelValue', 'entity')"
    >
      Entités
    </button>
  </div>
</template>
