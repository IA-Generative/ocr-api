<script setup lang="ts">
import type { CSSProperties } from 'vue'
import type { components } from '@/api/types/api.schema'
import { onBeforeUnmount, onMounted, ref } from 'vue'
import BboxDrawingOverlay from '@/components/BboxDrawingOverlay.vue'
import type { DrawnBox } from '@/composables/use-box-drawing'
import type { BoxMeta } from '@/composables/use-ocr-review'

type Bbox = components['schemas']['Bbox']

const props = defineProps<{
  allBoxes: (Bbox | DrawnBox)[]
  boxMeta: BoxMeta[]
  showImage: boolean
  drawingMode: boolean
  selectedBoxIdx: number | null
  imageUrl: string | undefined
  highlightedBoxIndices?: Set<number>
}>()

const emit = defineEmits<{
  select: [idx: number]
  toggleVisibility: [idx: number]
  drawn: [box: DrawnBox]
}>()

const imgRef = ref<HTMLImageElement | null>(null)
const imgDimensions = ref({ width: 0, height: 0 })
let resizeObserver: ResizeObserver

function styleForBox (box: Bbox): CSSProperties {
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
      imgDimensions.value = { width: contentRect.width, height: contentRect.height }
    }
  })
  resizeObserver.observe(imgRef.value)
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
})
</script>

<template>
  <div class="relative border border-slate-300">
    <img
      ref="imgRef"
      :src="imageUrl"
      alt="OCR page"
      class="block w-full h-auto transition-opacity duration-300"
      :class="showImage ? 'opacity-100' : 'opacity-0'"
    >

    <div
      v-for="(box, idx) in allBoxes"
      :key="idx"
      :style="styleForBox(box)"
      :class="[
        'group cursor-pointer',
        boxMeta[idx]?.hidden ? 'box-invisible' : (showImage ? 'box-visible' : 'box-hidden'),
        selectedBoxIdx === idx ? 'box-selected' : (highlightedBoxIndices?.has(idx) ? 'box-chat-highlight' : boxMeta[idx]?.reviewClass),
      ]"
      @click.stop="emit('select', idx)"
    >
      <span
        v-if="!showImage"
        class="text-xs font-bold text-black"
      >{{ boxMeta[idx]?.correctedText ?? box.text }}</span>
      <button
        class="absolute -top-3 -right-3 z-30 flex items-center justify-center w-5 h-5 rounded-full bg-white border border-slate-300 shadow opacity-0 group-hover:opacity-100 transition-opacity hover:bg-slate-100"
        :title="boxMeta[idx]?.hidden ? 'Afficher' : 'Masquer'"
        @click.stop="emit('toggleVisibility', idx)"
      >
        <span
          class="text-slate-500"
          :class="boxMeta[idx]?.hidden ? 'fr-icon-eye-line' : 'fr-icon-eye-off-line'"
          style="font-size: 10px;"
          aria-hidden="true"
        />
      </button>
    </div>

    <BboxDrawingOverlay
      v-if="drawingMode"
      @drawn="emit('drawn', $event)"
    />
  </div>
</template>

<style scoped>
.box-visible {
  position: absolute;
  background-color: rgba(20, 184, 166, 0.2);
  border: 1.5px solid rgba(20, 184, 166, 0.85);
}
.box-hidden {
  position: absolute;
  background-color: transparent;
  border: none;
}
.box-invisible {
  position: absolute;
  background-color: transparent;
  border: 1px dashed rgba(148, 163, 184, 0.5);
  opacity: 0.4;
}
.box-selected {
  background-color: rgba(37, 99, 235, 0.25) !important;
  border: 2px solid rgba(37, 99, 235, 0.9) !important;
  outline: 2px solid rgba(37, 99, 235, 0.4);
}
.box-reviewed-valid {
  background-color: rgba(16, 185, 129, 0.2) !important;
  border: 2px solid rgba(16, 185, 129, 0.8) !important;
}
.box-reviewed-invalid {
  background-color: rgba(239, 68, 68, 0.2) !important;
  border: 2px solid rgba(239, 68, 68, 0.8) !important;
}
.box-reviewed-corrected {
  background-color: rgba(245, 158, 11, 0.2) !important;
  border: 2px solid rgba(245, 158, 11, 0.8) !important;
}
.box-drawn {
  background-color: rgba(139, 92, 246, 0.2) !important;
  border: 2px dashed rgba(139, 92, 246, 0.9) !important;
}
.box-chat-highlight {
  background-color: rgba(234, 179, 8, 0.25) !important;
  border: 2px solid rgba(202, 138, 4, 0.9) !important;
  outline: 2px solid rgba(234, 179, 8, 0.4);
  animation: chat-pulse 1.5s ease-in-out 3;
}
@keyframes chat-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(234, 179, 8, 0.5); }
  50%       { box-shadow: 0 0 0 6px rgba(234, 179, 8, 0); }
}
</style>
