<script setup lang="ts">
import type { components } from '@/api/types/api.schema'
import type { BboxReview } from '@/interfaces/review'
import type { DrawnBox } from '@/composables/use-box-drawing'
import { computed } from 'vue'
import type { IoUResult } from '@/composables/use-ocr-metrics'
import { computeDocumentMetrics, computePageIoU } from '@/composables/use-ocr-metrics'

type Page = components['schemas']['Page']

const props = defineProps<{
  pages: Page[]
  corrections: Map<string, BboxReview>
  drawnBoxes: DrawnBox[]
  currentPage: number
}>()

const emit = defineEmits<{ close: [] }>()

const metrics = computed(() => computeDocumentMetrics(props.pages, props.corrections))

const iouResults = computed(() =>
  computePageIoU(props.pages[props.currentPage]?.boxes ?? [], props.drawnBoxes),
)

const avgIoU = computed(() => {
  if (!iouResults.value.length) return null
  return iouResults.value.reduce((s: number, r: IoUResult) => s + r.iou, 0) / iouResults.value.length
})

const mAP50 = computed(() => {
  if (!iouResults.value.length) return null
  return iouResults.value.filter((r: IoUResult) => r.iou >= 0.5).length / iouResults.value.length
})

function confidenceColor (c: number): string {
  if (c >= 0.9) return 'text-emerald-600'
  if (c >= 0.7) return 'text-amber-500'
  return 'text-red-500'
}

function pct (value: number, total: number): string {
  if (!total) return '0%'
  return `${Math.round((value / total) * 100)}%`
}
</script>

<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center p-4"
    @click.self="emit('close')"
  >
      <div
        class="relative bg-white/95 backdrop-blur-xl rounded-3xl shadow-[0_24px_80px_-12px_rgba(0,0,0,0.15)] w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col border border-white/60"
      >
        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100/80">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-sm">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4.5 h-4.5"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>
            </div>
            <div>
              <h2 class="text-base font-semibold text-slate-800">Métriques</h2>
              <p class="text-[11px] text-slate-400">{{ metrics.totalPages }} pages · {{ metrics.totalBoxes }} zones</p>
            </div>
          </div>
          <button
            class="w-7 h-7 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
            aria-label="Fermer"
            @click="emit('close')"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
          </button>
        </div>

        <!-- Content -->
        <div class="overflow-y-auto px-6 py-5 space-y-5 flex-1">

          <!-- KPI cards -->
          <div class="grid grid-cols-4 gap-2.5">
            <div class="rounded-2xl bg-gradient-to-br from-slate-50 to-slate-100/80 px-4 py-3.5 text-center border border-slate-100/50">
              <p class="text-[26px] font-extrabold text-slate-800 tabular-nums leading-none">{{ metrics.totalPages }}</p>
              <p class="text-[10px] font-medium text-slate-400 mt-1.5 uppercase tracking-wider">Pages</p>
            </div>
            <div class="rounded-2xl bg-gradient-to-br from-slate-50 to-slate-100/80 px-4 py-3.5 text-center border border-slate-100/50">
              <p class="text-[26px] font-extrabold text-slate-800 tabular-nums leading-none">{{ metrics.totalBoxes }}</p>
              <p class="text-[10px] font-medium text-slate-400 mt-1.5 uppercase tracking-wider">Zones OCR</p>
            </div>
            <div class="rounded-2xl px-4 py-3.5 text-center border"
              :class="metrics.avgConfidence >= 0.9 ? 'bg-gradient-to-br from-emerald-50 to-emerald-100/60 border-emerald-100/50' : metrics.avgConfidence >= 0.7 ? 'bg-gradient-to-br from-amber-50 to-amber-100/60 border-amber-100/50' : 'bg-gradient-to-br from-red-50 to-red-100/60 border-red-100/50'"
            >
              <p class="text-[26px] font-extrabold tabular-nums leading-none"
                :class="confidenceColor(metrics.avgConfidence)"
              >{{ (metrics.avgConfidence * 100).toFixed(0) }}<span class="text-base">%</span></p>
              <p class="text-[10px] font-medium text-slate-400 mt-1.5 uppercase tracking-wider">Confiance</p>
            </div>
            <div class="rounded-2xl bg-gradient-to-br from-blue-50 to-indigo-100/40 px-4 py-3.5 text-center border border-blue-100/50">
              <p class="text-[26px] font-extrabold text-blue-600 tabular-nums leading-none">{{ (metrics.reviewCoverage * 100).toFixed(0) }}<span class="text-base">%</span></p>
              <p class="text-[10px] font-medium text-slate-400 mt-1.5 uppercase tracking-wider">Révisé</p>
            </div>
          </div>

          <!-- Confidence distribution -->
          <div class="rounded-2xl border border-slate-100 bg-white px-5 py-4">
            <h3 class="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Distribution de la confiance</h3>
            <div class="flex rounded-full overflow-hidden h-2.5 w-full bg-slate-100">
              <div class="bg-red-400 transition-all duration-500" :style="{ width: pct(metrics.lowConfidenceCount, metrics.totalBoxes) }" />
              <div class="bg-amber-400 transition-all duration-500" :style="{ width: pct(metrics.mediumConfidenceCount, metrics.totalBoxes) }" />
              <div class="bg-emerald-400 transition-all duration-500" :style="{ width: pct(metrics.highConfidenceCount, metrics.totalBoxes) }" />
            </div>
            <div class="flex gap-5 mt-2.5 text-[11px] text-slate-500">
              <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-red-400" /> &lt;70% · {{ metrics.lowConfidenceCount }}</span>
              <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-amber-400" /> 70–90% · {{ metrics.mediumConfidenceCount }}</span>
              <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-emerald-400" /> ≥90% · {{ metrics.highConfidenceCount }}</span>
            </div>
          </div>

          <!-- Review breakdown -->
          <div class="rounded-2xl border border-slate-100 bg-white px-5 py-4">
            <h3 class="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Résumé de révision</h3>
            <div class="grid grid-cols-4 gap-2">
              <div class="rounded-xl bg-slate-50 px-3 py-2.5 text-center">
                <p class="text-lg font-bold text-slate-500 tabular-nums">{{ metrics.totalBoxes - metrics.reviewedCount }}</p>
                <p class="text-[10px] text-slate-400 mt-0.5">Non révisées</p>
              </div>
              <div class="rounded-xl bg-emerald-50 px-3 py-2.5 text-center">
                <p class="text-lg font-bold text-emerald-600 tabular-nums">{{ metrics.validCount }}</p>
                <p class="text-[10px] text-emerald-500 mt-0.5">Valides</p>
              </div>
              <div class="rounded-xl bg-amber-50 px-3 py-2.5 text-center">
                <p class="text-lg font-bold text-amber-600 tabular-nums">{{ metrics.correctedCount }}</p>
                <p class="text-[10px] text-amber-500 mt-0.5">Corrigées</p>
              </div>
              <div class="rounded-xl bg-red-50 px-3 py-2.5 text-center">
                <p class="text-lg font-bold text-red-500 tabular-nums">{{ metrics.invalidCount }}</p>
                <p class="text-[10px] text-red-400 mt-0.5">Invalides</p>
              </div>
            </div>
            <p v-if="metrics.validCount + metrics.invalidCount > 0" class="mt-3 text-[11px] text-slate-400">
              Précision estimée : <span class="font-semibold text-slate-600">{{ (metrics.precision * 100).toFixed(1) }}%</span>
            </p>
          </div>

          <!-- IoU section -->
          <div class="rounded-2xl border border-slate-100 bg-white px-5 py-4">
            <div class="flex items-center justify-between mb-3">
              <h3 class="text-xs font-semibold text-slate-500 uppercase tracking-wider">IoU — Page {{ currentPage + 1 }}</h3>
              <div v-if="iouResults.length > 0" class="flex gap-3 text-[11px]">
                <span class="text-slate-400">Moy. <span class="font-semibold" :class="avgIoU !== null && avgIoU >= 0.5 ? 'text-emerald-600' : 'text-amber-500'">{{ avgIoU !== null ? (avgIoU * 100).toFixed(0) + '%' : '—' }}</span></span>
                <span class="text-slate-400">mAP@50 <span class="font-semibold" :class="mAP50 !== null && mAP50 >= 0.5 ? 'text-emerald-600' : 'text-amber-500'">{{ mAP50 !== null ? (mAP50 * 100).toFixed(0) + '%' : '—' }}</span></span>
              </div>
            </div>
            <div v-if="iouResults.length > 0" class="space-y-1.5">
              <div
                v-for="r in iouResults"
                :key="r.drawnBoxIdx"
                class="flex items-center gap-3 rounded-xl bg-slate-50 px-3 py-2"
              >
                <span class="text-[11px] font-semibold text-violet-600 w-20 shrink-0">Zone {{ r.drawnBoxIdx + 1 }}</span>
                <span class="flex-1 text-[11px] text-slate-500 truncate">{{ r.nearestOcrText || '—' }}</span>
                <div class="w-16 h-1.5 bg-slate-200 rounded-full overflow-hidden shrink-0">
                  <div
                    class="h-full rounded-full transition-all duration-500"
                    :class="r.iou >= 0.5 ? 'bg-emerald-400' : r.iou >= 0.2 ? 'bg-amber-400' : 'bg-red-400'"
                    :style="{ width: `${(r.iou * 100).toFixed(0)}%` }"
                  />
                </div>
                <span class="text-[11px] font-mono font-semibold w-10 text-right tabular-nums"
                  :class="r.iou >= 0.5 ? 'text-emerald-600' : r.iou >= 0.2 ? 'text-amber-500' : 'text-red-500'"
                >{{ (r.iou * 100).toFixed(0) }}%</span>
              </div>
            </div>
            <div v-else class="py-6 text-center text-[11px] text-slate-400">
              Dessinez des zones sur cette page pour voir les métriques IoU.
            </div>
          </div>

          <!-- Per-page table -->
          <div class="rounded-2xl border border-slate-100 bg-white overflow-hidden">
            <div class="px-5 py-3 border-b border-slate-50">
              <h3 class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Détail par page</h3>
            </div>
            <table class="w-full text-[11px]">
              <thead>
                <tr class="text-slate-400 border-b border-slate-50">
                  <th class="text-left px-4 py-2 font-medium">Page</th>
                  <th class="text-right px-4 py-2 font-medium">Zones</th>
                  <th class="text-right px-4 py-2 font-medium">Confiance</th>
                  <th class="text-right px-4 py-2 font-medium">Révision</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="pg in metrics.pages"
                  :key="pg.pageIdx"
                  class="border-b border-slate-50/80 last:border-0 transition-colors"
                  :class="pg.pageIdx === currentPage ? 'bg-blue-50/60' : 'hover:bg-slate-50/50'"
                >
                  <td class="px-4 py-2.5 font-medium text-slate-700">
                    {{ pg.pageIdx + 1 }}
                    <span v-if="pg.pageIdx === currentPage" class="ml-1 text-[9px] font-semibold text-blue-500 bg-blue-100 px-1.5 py-0.5 rounded-full">actuelle</span>
                  </td>
                  <td class="px-4 py-2.5 text-right text-slate-500 tabular-nums">{{ pg.totalBoxes }}</td>
                  <td class="px-4 py-2.5 text-right tabular-nums">
                    <span :class="confidenceColor(pg.avgConfidence)">{{ (pg.avgConfidence * 100).toFixed(0) }}%</span>
                  </td>
                  <td class="px-4 py-2.5 text-right tabular-nums">
                    <span class="text-slate-400">{{ pg.reviewedCount }}/{{ pg.totalBoxes }}</span>
                    <span v-if="pg.validCount" class="ml-1.5 text-emerald-500">✓{{ pg.validCount }}</span>
                    <span v-if="pg.invalidCount" class="ml-1 text-red-400">✗{{ pg.invalidCount }}</span>
                    <span v-if="pg.correctedCount" class="ml-1 text-amber-500">~{{ pg.correctedCount }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

        </div>
      </div>
  </div>
</template>
