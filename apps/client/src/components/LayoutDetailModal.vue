<script setup lang="ts">
import { computed } from 'vue'
import type { components } from '@/api/types/api.schema'
import type { FormulaBlock, TableBlock, ImageBlock } from './layout/types'
import LayoutBlockFormula from './layout/LayoutBlockFormula.vue'
import LayoutBlockTable from './layout/LayoutBlockTable.vue'
import LayoutBlockImage from './layout/LayoutBlockImage.vue'

type Layout = components['schemas']['Layout-Output']

const props = defineProps<{
  layout: Layout
}>()

const emit = defineEmits<{
  close: []
}>()

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
  display_formula: { bg: 'rgba(239,68,68,0.12)', border: 'rgba(239,68,68,0.75)', text: 'rgb(185,28,28)' },
  algorithm: { bg: 'rgba(245,158,11,0.12)', border: 'rgba(245,158,11,0.75)', text: 'rgb(180,83,9)' },
}
const LAYOUT_DEFAULT_COLOR = { bg: 'rgba(100,116,139,0.12)', border: 'rgba(100,116,139,0.75)', text: 'rgb(51,65,85)' }

const color = computed(() => LAYOUT_COLORS[props.layout.label?.toLowerCase()] ?? LAYOUT_DEFAULT_COLOR)
const scorePercent = computed(() => Math.round(props.layout.score * 100))

const [xmin, ymin, xmax, ymax] = props.layout.coordinate
const width = Math.round(xmax - xmin)
const height = Math.round(ymax - ymin)

const labelLower = computed(() => props.layout.label?.toLowerCase())
const isFormula = computed(() => labelLower.value === 'formula' || labelLower.value === 'display_formula')
const isTable = computed(() => labelLower.value === 'table' || labelLower.value === 'table_caption')
const isFigure = computed(() => labelLower.value === 'figure' || labelLower.value === 'figure_caption' || labelLower.value === 'image')

const formulaBlock = computed<FormulaBlock | null>(() => {
  const raw = props.layout.block ?? props.layout.content
  return isFormula.value && raw ? (raw as FormulaBlock) : null
})
const tableBlock = computed<TableBlock | null>(() => {
  const raw = props.layout.block ?? props.layout.content
  return isTable.value && raw ? (raw as TableBlock) : null
})
const imageBlock = computed<ImageBlock | null>(() => {
  const raw = props.layout.block ?? props.layout.content
  return isFigure.value && raw ? (raw as ImageBlock) : null
})

const isWide = computed(() => isTable.value || isFigure.value)
</script>

<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 z-50 flex items-center justify-center"
      style="background-color: rgba(0, 0, 0, 0.4)"
      @click.self="emit('close')"
    >
      <div
        class="relative bg-white rounded-2xl shadow-2xl mx-4 overflow-hidden"
        :class="isWide ? 'w-full max-w-2xl' : 'w-full max-w-sm'"
      >
        <!-- Header -->
        <div
          class="px-5 py-4 flex items-center gap-3"
          :style="{ backgroundColor: color.bg, borderBottom: `2px solid ${color.border}` }"
        >
          <span
            class="text-sm font-bold px-3 py-1 rounded-full text-white"
            :style="{ backgroundColor: color.border }"
          >{{ layout.label }}</span>
          <span class="text-xs font-medium" :style="{ color: color.text }">
            Classe #{{ layout.cls_id }}
          </span>
          <button
            class="text-slate-400 hover:text-slate-600 transition-colors"
            style="margin-left: auto; flex-shrink: 0"
            aria-label="Fermer"
            @click="emit('close')"
          >
            <span class="fr-icon-close-line" style="font-size:18px" aria-hidden="true" />
          </button>
        </div>

        <!-- Body -->
        <div class="p-5 flex flex-col gap-4 max-h-[80vh] overflow-y-auto">

          <!-- Confiance -->
          <div class="flex flex-col gap-1.5">
            <div class="flex justify-between items-center text-sm">
              <span class="font-medium text-slate-600">Confiance</span>
              <span
                class="font-bold text-sm"
                :class="scorePercent >= 80 ? 'text-emerald-600' : scorePercent >= 50 ? 'text-amber-500' : 'text-red-500'"
              >{{ scorePercent }}%</span>
            </div>
            <div class="h-2 rounded-full bg-slate-100 overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-500"
                :class="scorePercent >= 80 ? 'bg-emerald-500' : scorePercent >= 50 ? 'bg-amber-400' : 'bg-red-400'"
                :style="{ width: `${scorePercent}%` }"
              />
            </div>
          </div>

          <!-- Coordonnées -->
          <div class="rounded-xl border border-slate-100 bg-slate-50 px-4 py-3 flex flex-col gap-2">
            <p class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Coordonnées</p>
            <div class="grid grid-cols-2 gap-x-4 gap-y-1.5 text-xs text-slate-700">
              <div class="flex justify-between">
                <span class="text-slate-400">x min</span>
                <span class="font-mono font-medium">{{ Math.round(xmin) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-400">y min</span>
                <span class="font-mono font-medium">{{ Math.round(ymin) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-400">x max</span>
                <span class="font-mono font-medium">{{ Math.round(xmax) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-400">y max</span>
                <span class="font-mono font-medium">{{ Math.round(ymax) }}</span>
              </div>
              <div class="flex justify-between col-span-2 pt-1 border-t border-slate-200 mt-0.5">
                <span class="text-slate-400">Taille</span>
                <span class="font-mono font-medium">{{ width }} × {{ height }} px</span>
              </div>
            </div>
          </div>

          <!-- Ordre de lecture -->
          <div v-if="layout.order != null" class="flex items-center justify-between text-sm">
            <span class="font-medium text-slate-600">Ordre de lecture</span>
            <span class="font-mono font-bold text-slate-700 bg-slate-100 px-2.5 py-0.5 rounded-full">#{{ layout.order }}</span>
          </div>

          <!-- Bloc spécialisé -->
          <LayoutBlockFormula v-if="formulaBlock" :block="formulaBlock" />
          <LayoutBlockTable v-else-if="tableBlock" :block="tableBlock" />
          <LayoutBlockImage v-else-if="imageBlock" :block="imageBlock" />

          <!-- Contenu texte générique -->
          <div v-else-if="layout.content" class="flex flex-col gap-1.5">
            <p class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Contenu</p>
            <div class="rounded-xl border border-slate-100 bg-slate-50 px-3 py-2.5 text-xs text-slate-700 max-h-32 overflow-y-auto leading-relaxed whitespace-pre-wrap break-words">
              {{ typeof layout.content === 'string' ? layout.content : JSON.stringify(layout.content, null, 2) }}
            </div>
          </div>

        </div>
      </div>
    </div>
  </Teleport>
</template>
