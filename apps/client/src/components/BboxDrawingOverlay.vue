<script setup lang="ts">
import { useBoxDrawing } from '@/composables/use-box-drawing'
import type { DrawnBox } from '@/composables/use-box-drawing'
import { ref } from 'vue'

const emit = defineEmits<{
  drawn: [box: DrawnBox]
}>()

const containerRef = ref<HTMLDivElement | null>(null)

const { isDrawing, previewRect, onMouseDown, onMouseMove, onMouseUp, cancel } = useBoxDrawing(
  (box) => emit('drawn', box),
)

function handleMouseDown (e: MouseEvent) {
  if (containerRef.value) onMouseDown(e, containerRef.value)
}
function handleMouseMove (e: MouseEvent) {
  if (containerRef.value) onMouseMove(e, containerRef.value)
}
function handleMouseUp (e: MouseEvent) {
  if (containerRef.value) onMouseUp(e, containerRef.value)
}
</script>

<template>
  <div
    ref="containerRef"
    class="absolute inset-0 z-30"
    :class="isDrawing ? 'cursor-crosshair' : 'cursor-crosshair'"
    @mousedown.prevent="handleMouseDown"
    @mousemove="handleMouseMove"
    @mouseup="handleMouseUp"
    @mouseleave="cancel"
  >
    <!-- Preview rectangle while drawing -->
    <div
      v-if="previewRect"
      class="absolute pointer-events-none border-2 border-dashed border-violet-500 bg-violet-200/30"
      :style="{
        left: `${previewRect.x * 100}%`,
        top: `${previewRect.y * 100}%`,
        width: `${previewRect.w * 100}%`,
        height: `${previewRect.h * 100}%`,
      }"
    />
  </div>
</template>
