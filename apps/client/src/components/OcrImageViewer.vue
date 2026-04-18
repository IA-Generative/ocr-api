<script setup lang="ts">
import type { CSSProperties } from 'vue'
import type { components } from '@/api/types/api.schema'
import { onBeforeUnmount, onMounted, ref } from 'vue'
import BboxDrawingOverlay from '@/components/BboxDrawingOverlay.vue'
import EntityDetailModal from '@/components/EntityDetailModal.vue'
import LayoutDetailModal from '@/components/LayoutDetailModal.vue'
import type { DrawnBox } from '@/composables/use-box-drawing'
import type { BoxMeta } from '@/composables/use-ocr-review'

type Bbox = components['schemas']['Bbox']
type Layout = components['schemas']['Layout']
type EntityPrediction = {
  entity_name: string
  confidence: number
  value?: string | null
  bbox?: Bbox[] | null
}

const props = defineProps<{
  allBoxes: (Bbox | DrawnBox)[]
  boxMeta: BoxMeta[]
  showImage: boolean
  drawingMode: boolean
  selectedBoxIdx: number | null
  imageUrl: string | undefined
  highlightedBoxIndices?: Set<number>
  viewMode?: 'ocr' | 'layout' | 'entity'
  layoutBoxes?: Layout[]
  entityBoxes?: EntityPrediction[]
  entitySearchMatchIndices?: Set<number>
  dimmedWhenSearch?: boolean
}>()

const emit = defineEmits<{
  select: [idx: number]
  toggleVisibility: [idx: number]
  drawn: [box: DrawnBox]
}>()

const imgRef = ref<HTMLImageElement | null>(null)
const imgDimensions = ref({ width: 0, height: 0 })
const imgNatural = ref({ width: 0, height: 0 })
let resizeObserver: ResizeObserver

function onImageLoad () {
  if (!imgRef.value) return
  imgDimensions.value = { width: imgRef.value.clientWidth, height: imgRef.value.clientHeight }
  imgNatural.value = { width: imgRef.value.naturalWidth, height: imgRef.value.naturalHeight }
}

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

function styleForLayout (layout: Layout): CSSProperties {
  const W = imgDimensions.value.width
  const H = imgDimensions.value.height
  const NW = imgNatural.value.width || W
  const NH = imgNatural.value.height || H
  const scaleX = W / NW
  const scaleY = H / NH
  const [xmin, ymin, xmax, ymax] = layout.coordinate
  return {
    position: 'absolute',
    left: `${xmin * scaleX}px`,
    top: `${ymin * scaleY}px`,
    width: `${(xmax - xmin) * scaleX}px`,
    height: `${(ymax - ymin) * scaleY}px`,
    zIndex: 20,
  }
}

function styleForEntity (bbox: Bbox): CSSProperties {
  const W = imgDimensions.value.width
  const H = imgDimensions.value.height
  return {
    position: 'absolute',
    left: `${bbox.x * W}px`,
    top: `${bbox.y * H}px`,
    width: `${bbox.width * W}px`,
    height: `${bbox.height * H}px`,
    zIndex: 20,
  }
}

const ENTITY_COLORS = [
  { bg: 'rgba(239,68,68,0.15)',   border: 'rgba(239,68,68,0.85)',   badge: '#dc2626' },
  { bg: 'rgba(249,115,22,0.15)',  border: 'rgba(249,115,22,0.85)',  badge: '#ea580c' },
  { bg: 'rgba(234,179,8,0.15)',   border: 'rgba(234,179,8,0.85)',   badge: '#ca8a04' },
  { bg: 'rgba(34,197,94,0.15)',   border: 'rgba(34,197,94,0.85)',   badge: '#16a34a' },
  { bg: 'rgba(6,182,212,0.15)',   border: 'rgba(6,182,212,0.85)',   badge: '#0891b2' },
  { bg: 'rgba(99,102,241,0.15)',  border: 'rgba(99,102,241,0.85)',  badge: '#4f46e5' },
  { bg: 'rgba(217,70,239,0.15)',  border: 'rgba(217,70,239,0.85)',  badge: '#a21caf' },
  { bg: 'rgba(244,63,94,0.15)',   border: 'rgba(244,63,94,0.85)',   badge: '#e11d48' },
]

const entityColorMap = new Map<string, typeof ENTITY_COLORS[number]>()
function getEntityColor (name: string) {
  if (!entityColorMap.has(name)) {
    entityColorMap.set(name, ENTITY_COLORS[entityColorMap.size % ENTITY_COLORS.length])
  }
  return entityColorMap.get(name)!
}

const LAYOUT_COLORS: Record<string, { bg: string; border: string; text: string }> = {
  text: { bg: 'rgba(59,130,246,0.12)', border: 'rgba(59,130,246,0.75)', text: 'rgb(29,78,216)' },
  paragraph_title: { bg: 'rgba(168,85,247,0.12)', border: 'rgba(168,85,247,0.75)', text: 'rgb(126,34,206)' },
  doc_title: { bg: 'rgba(217,70,239,0.12)', border: 'rgba(217,70,239,0.75)', text: 'rgb(162,28,175)' },
  figure: { bg: 'rgba(249,115,22,0.12)', border: 'rgba(249,115,22,0.75)', text: 'rgb(194,65,12)' },
  figure_caption: { bg: 'rgba(251,146,60,0.12)', border: 'rgba(251,146,60,0.75)', text: 'rgb(180,83,9)' },
  table: { bg: 'rgba(16,185,129,0.12)', border: 'rgba(16,185,129,0.75)', text: 'rgb(6,95,70)' },
  table_caption: { bg: 'rgba(52,211,153,0.12)', border: 'rgba(52,211,153,0.75)', text: 'rgb(6,95,70)' },
  header: { bg: 'rgba(148,163,184,0.12)', border: 'rgba(148,163,184,0.75)', text: 'rgb(71,85,105)' },
  footer: { bg: 'rgba(148,163,184,0.12)', border: 'rgba(148,163,184,0.75)', text: 'rgb(71,85,105)' },
  reference: { bg: 'rgba(156,163,175,0.12)', border: 'rgba(156,163,175,0.75)', text: 'rgb(75,85,99)' },
  formula: { bg: 'rgba(239,68,68,0.12)', border: 'rgba(239,68,68,0.75)', text: 'rgb(185,28,28)' },
  algorithm: { bg: 'rgba(245,158,11,0.12)', border: 'rgba(245,158,11,0.75)', text: 'rgb(180,83,9)' },
}
const LAYOUT_DEFAULT_COLOR = { bg: 'rgba(100,116,139,0.12)', border: 'rgba(100,116,139,0.75)', text: 'rgb(51,65,85)' }

function getLayoutColor (label: string) {
  return LAYOUT_COLORS[label?.toLowerCase()] ?? LAYOUT_DEFAULT_COLOR
}

const selectedLayout = ref<Layout | null>(null)
const selectedEntity = ref<{ entity: EntityPrediction; colorIndex: number } | null>(null)

onMounted(() => {
  if (!imgRef.value) return
  imgDimensions.value = { width: imgRef.value.clientWidth, height: imgRef.value.clientHeight }
  if (imgRef.value.naturalWidth > 0) {
    imgNatural.value = { width: imgRef.value.naturalWidth, height: imgRef.value.naturalHeight }
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
      @load="onImageLoad"
    >

    <!-- OCR boxes -->
    <template v-if="!viewMode || viewMode === 'ocr'">
      <div
        v-for="(box, idx) in allBoxes"
        :key="idx"
        :style="styleForBox(box)"
        :class="[
          'group cursor-pointer transition-opacity duration-150',
          boxMeta[idx]?.hidden ? 'box-invisible' : (showImage ? 'box-visible' : 'box-hidden'),
          selectedBoxIdx === idx ? 'box-selected'
            : highlightedBoxIndices?.has(idx) ? 'box-search-highlight'
            : boxMeta[idx]?.reviewClass,
          dimmedWhenSearch && !highlightedBoxIndices?.has(idx) && selectedBoxIdx !== idx
            ? 'opacity-20'
            : '',
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
    </template>

    <!-- Layout boxes -->
    <template v-else-if="viewMode === 'layout'">
      <div
        v-for="(layout, idx) in (layoutBoxes ?? [])"
        :key="`layout-${idx}`"
        :style="{
          ...styleForLayout(layout),
          backgroundColor: getLayoutColor(layout.label).bg,
          border: `1.5px solid ${getLayoutColor(layout.label).border}`,
        }"
        class="layout-box group cursor-pointer"
        :title="`${layout.label} — score : ${Math.round(layout.score * 100)} %`"
        @click.stop="selectedLayout = layout"
      >
        <span
          class="layout-label-badge"
          :style="{ backgroundColor: getLayoutColor(layout.label).border, color: '#fff' }"
        >{{ layout.label }}</span>
      </div>
    </template>

    <!-- Entity boxes -->
    <template v-else-if="viewMode === 'entity'">
      <template v-for="(entity, eIdx) in (entityBoxes ?? [])" :key="`entity-${eIdx}`">
        <div
          v-for="(bbox, bIdx) in (entity.bbox ?? [])"
          :key="`entity-${eIdx}-${bIdx}`"
          :style="{
            ...styleForEntity(bbox),
            backgroundColor: getEntityColor(entity.entity_name).bg,
            border: `1.5px solid ${getEntityColor(entity.entity_name).border}`,
            opacity: entitySearchMatchIndices && !entitySearchMatchIndices.has(eIdx) ? 0.15 : 1,
          }"
          class="entity-box group transition-opacity duration-150 cursor-pointer"
          :title="`${entity.entity_name}${entity.value ? ' : ' + entity.value : ''} (${Math.round(entity.confidence * 100)} %)`"
          @click.stop="selectedEntity = { entity, colorIndex: eIdx }"
        >
          <span
            class="entity-label-badge"
            :style="{ backgroundColor: getEntityColor(entity.entity_name).badge, color: '#fff' }"
          >{{ entity.entity_name }}</span>
        </div>
      </template>
    </template>

    <BboxDrawingOverlay
      v-if="drawingMode && (!viewMode || viewMode === 'ocr')"
      @drawn="emit('drawn', $event)"
    />

    <LayoutDetailModal
      v-if="selectedLayout"
      :layout="selectedLayout"
      @close="selectedLayout = null"
    />

    <EntityDetailModal
      v-if="selectedEntity"
      :entity="selectedEntity.entity"
      :color-index="selectedEntity.colorIndex"
      @close="selectedEntity = null"
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
.box-search-highlight {
  background-color: rgba(234, 179, 8, 0.35) !important;
  border: 2px solid rgba(202, 138, 4, 0.95) !important;
  outline: 2px solid rgba(234, 179, 8, 0.5);
}
@keyframes chat-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(234, 179, 8, 0.5); }
  50%       { box-shadow: 0 0 0 6px rgba(234, 179, 8, 0); }
}
.layout-box {
  position: absolute;
  cursor: default;
}
.layout-label-badge {
  position: absolute;
  top: 0;
  left: 0;
  font-size: 9px;
  font-weight: 600;
  line-height: 1;
  padding: 1px 4px;
  border-radius: 0 0 4px 0;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.15s;
  white-space: nowrap;
}
.layout-box:hover .layout-label-badge {
  opacity: 1;
}
.entity-box {
  position: absolute;
  cursor: default;
}
.entity-label-badge {
  position: absolute;
  top: 0;
  left: 0;
  font-size: 9px;
  font-weight: 600;
  line-height: 1;
  padding: 1px 4px;
  border-radius: 0 0 4px 0;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.15s;
  white-space: nowrap;
}
.entity-box:hover .entity-label-badge {
  opacity: 1;
}
</style>
