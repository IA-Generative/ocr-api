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
  <Teleport to="body">
    <div
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
      @click.self="emit('close')"
    >
      <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <div class="flex items-center gap-2">
            <span class="fr-icon-bar-chart-box-line text-blue-600" aria-hidden="true" />
            <h2 class="text-lg font-semibold text-slate-800">
              Métriques du document
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

        <!-- Content -->
        <div class="overflow-y-auto px-6 py-5 space-y-6 flex-1">
          <!-- Stat cards -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div class="rounded-xl border border-slate-100 bg-slate-50 px-4 py-3 text-center">
              <p class="text-2xl font-bold text-slate-800">
                {{ metrics.totalPages }}
              </p>
              <p class="text-xs text-slate-500 mt-0.5">
                Pages
              </p>
            </div>
            <div class="rounded-xl border border-slate-100 bg-slate-50 px-4 py-3 text-center">
              <p class="text-2xl font-bold text-slate-800">
                {{ metrics.totalBoxes }}
              </p>
              <p class="text-xs text-slate-500 mt-0.5">
                Zones OCR
              </p>
            </div>
            <div class="rounded-xl border border-slate-100 bg-slate-50 px-4 py-3 text-center">
              <p
                class="text-2xl font-bold"
                :class="confidenceColor(metrics.avgConfidence)"
              >
                {{ (metrics.avgConfidence * 100).toFixed(1) }}%
              </p>
              <p class="text-xs text-slate-500 mt-0.5">
                Conf. moyenne
              </p>
            </div>
            <div class="rounded-xl border border-slate-100 bg-slate-50 px-4 py-3 text-center">
              <p class="text-2xl font-bold text-blue-600">
                {{ (metrics.reviewCoverage * 100).toFixed(0) }}%
              </p>
              <p class="text-xs text-slate-500 mt-0.5">
                Révisé
              </p>
            </div>
          </div>

          <!-- Confidence distribution -->
          <div>
            <h3 class="text-sm font-semibold text-slate-700 mb-2">
              Distribution de la confiance
            </h3>
            <div class="flex rounded-full overflow-hidden h-4 w-full">
              <div
                class="bg-red-400 transition-all"
                :style="{ width: pct(metrics.lowConfidenceCount, metrics.totalBoxes) }"
                :title="`Faible < 70% : ${metrics.lowConfidenceCount}`"
              />
              <div
                class="bg-amber-400 transition-all"
                :style="{ width: pct(metrics.mediumConfidenceCount, metrics.totalBoxes) }"
                :title="`Moyen 70–90% : ${metrics.mediumConfidenceCount}`"
              />
              <div
                class="bg-emerald-400 transition-all"
                :style="{ width: pct(metrics.highConfidenceCount, metrics.totalBoxes) }"
                :title="`Élevé ≥ 90% : ${metrics.highConfidenceCount}`"
              />
            </div>
            <div class="flex gap-4 mt-2 text-xs text-slate-500">
              <span class="flex items-center gap-1">
                <span class="w-3 h-3 rounded-full bg-red-400 inline-block" /> Faible &lt;70% ({{ metrics.lowConfidenceCount }})
              </span>
              <span class="flex items-center gap-1">
                <span class="w-3 h-3 rounded-full bg-amber-400 inline-block" /> Moyen 70–90% ({{ metrics.mediumConfidenceCount }})
              </span>
              <span class="flex items-center gap-1">
                <span class="w-3 h-3 rounded-full bg-emerald-400 inline-block" /> Élevé ≥90% ({{ metrics.highConfidenceCount }})
              </span>
            </div>
          </div>

          <!-- Review breakdown -->
          <div>
            <h3 class="text-sm font-semibold text-slate-700 mb-2">
              Résumé de révision
            </h3>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
              <div class="rounded-lg bg-slate-100 px-3 py-2 flex flex-col gap-0.5">
                <span class="font-semibold text-slate-500">Non révisées</span>
                <span class="text-xl font-bold text-slate-600">{{ metrics.totalBoxes - metrics.reviewedCount }}</span>
              </div>
              <div class="rounded-lg bg-emerald-50 px-3 py-2 flex flex-col gap-0.5">
                <span class="font-semibold text-emerald-600">Valides</span>
                <span class="text-xl font-bold text-emerald-700">{{ metrics.validCount }}</span>
              </div>
              <div class="rounded-lg bg-amber-50 px-3 py-2 flex flex-col gap-0.5">
                <span class="font-semibold text-amber-600">Corrigées</span>
                <span class="text-xl font-bold text-amber-700">{{ metrics.correctedCount }}</span>
              </div>
              <div class="rounded-lg bg-red-50 px-3 py-2 flex flex-col gap-0.5">
                <span class="font-semibold text-red-600">Invalides</span>
                <span class="text-xl font-bold text-red-700">{{ metrics.invalidCount }}</span>
              </div>
            </div>
            <div
              v-if="metrics.validCount + metrics.invalidCount > 0"
              class="mt-2 text-xs text-slate-500"
            >
              Précision estimée (Valides / Révisées avec verdict) :
              <span class="font-semibold text-slate-700">{{ (metrics.precision * 100).toFixed(1) }}%</span>
            </div>
          </div>

          <!-- IoU section (current page, drawn boxes only) -->
          <div v-if="iouResults.length > 0">
            <h3 class="text-sm font-semibold text-slate-700 mb-2">
              IoU — Zones annotées vs OCR (page {{ currentPage + 1 }})
            </h3>
            <div class="flex gap-4 mb-3 text-xs text-slate-500">
              <span>
                IoU moyen :
                <span
                  class="font-bold"
                  :class="avgIoU !== null && avgIoU >= 0.5 ? 'text-emerald-600' : 'text-amber-500'"
                >{{ avgIoU !== null ? (avgIoU * 100).toFixed(1) + '%' : '—' }}</span>
              </span>
              <span>
                mAP@50 :
                <span
                  class="font-bold"
                  :class="mAP50 !== null && mAP50 >= 0.5 ? 'text-emerald-600' : 'text-amber-500'"
                >{{ mAP50 !== null ? (mAP50 * 100).toFixed(1) + '%' : '—' }}</span>
              </span>
            </div>
            <div class="rounded-xl border border-slate-100 overflow-hidden">
              <table class="w-full text-xs">
                <thead>
                  <tr class="bg-slate-50 border-b border-slate-100 text-slate-500">
                    <th class="text-left px-3 py-2">
                      Zone annotée
                    </th>
                    <th class="text-left px-3 py-2">
                      Zone OCR la plus proche
                    </th>
                    <th class="text-right px-3 py-2">
                      IoU
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="r in iouResults"
                    :key="r.drawnBoxIdx"
                    class="border-b border-slate-50 last:border-0"
                  >
                    <td class="px-3 py-2 font-medium text-violet-700">
                      Annotation {{ r.drawnBoxIdx + 1 }}
                    </td>
                    <td class="px-3 py-2 text-slate-500 truncate max-w-[200px]">
                      {{ r.nearestOcrText || '—' }}
                    </td>
                    <td class="px-3 py-2 text-right font-mono">
                      <span
                        class="inline-block px-2 py-0.5 rounded-full text-xs font-semibold"
                        :class="r.iou >= 0.5
                          ? 'bg-emerald-100 text-emerald-700'
                          : r.iou >= 0.2
                            ? 'bg-amber-100 text-amber-700'
                            : 'bg-red-100 text-red-600'"
                      >
                        {{ (r.iou * 100).toFixed(1) }}%
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div
            v-else
            class="rounded-xl border border-dashed border-slate-200 px-4 py-6 text-center text-xs text-slate-400"
          >
            Aucune zone annotée manuellement sur cette page — dessinez des zones pour voir les métriques IoU.
          </div>

          <!-- Per-page table -->
          <div>
            <h3 class="text-sm font-semibold text-slate-700 mb-2">
              Détail par page
            </h3>
            <div class="rounded-xl border border-slate-100 overflow-hidden">
              <table class="w-full text-xs">
                <thead>
                  <tr class="bg-slate-50 border-b border-slate-100 text-slate-500">
                    <th class="text-left px-3 py-2">
                      Page
                    </th>
                    <th class="text-right px-3 py-2">
                      Zones
                    </th>
                    <th class="text-right px-3 py-2">
                      Conf. moy.
                    </th>
                    <th class="text-right px-3 py-2">
                      Révision
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="pg in metrics.pages"
                    :key="pg.pageIdx"
                    class="border-b border-slate-50 last:border-0"
                    :class="pg.pageIdx === currentPage ? 'bg-blue-50' : ''"
                  >
                    <td class="px-3 py-2 font-medium text-slate-700">
                      Page {{ pg.pageIdx + 1 }}
                      <span
                        v-if="pg.pageIdx === currentPage"
                        class="ml-1 text-blue-500 text-[10px]"
                      >(actuelle)</span>
                    </td>
                    <td class="px-3 py-2 text-right text-slate-500">
                      {{ pg.totalBoxes }}
                    </td>
                    <td class="px-3 py-2 text-right">
                      <span :class="confidenceColor(pg.avgConfidence)">
                        {{ (pg.avgConfidence * 100).toFixed(1) }}%
                      </span>
                    </td>
                    <td class="px-3 py-2 text-right">
                      <span class="text-slate-400">{{ pg.reviewedCount }}/{{ pg.totalBoxes }}</span>
                      <span
                        v-if="pg.validCount"
                        class="ml-1 text-emerald-600"
                      >✓{{ pg.validCount }}</span>
                      <span
                        v-if="pg.invalidCount"
                        class="ml-1 text-red-500"
                      >✗{{ pg.invalidCount }}</span>
                      <span
                        v-if="pg.correctedCount"
                        class="ml-1 text-amber-500"
                      >~{{ pg.correctedCount }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
