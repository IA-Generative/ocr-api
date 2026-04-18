<script setup lang="ts">
import type { components } from '@/api/types/api.schema'
import { computed } from 'vue'

type Bbox = components['schemas']['Bbox']

export type EntityPrediction = {
  entity_name: string
  confidence: number
  value?: string | null
  bbox?: Bbox[] | null
  pages?: number[] | null
}

const ENTITY_COLORS = [
  { bg: 'rgba(239,68,68,0.10)', border: 'rgba(239,68,68,0.85)', badge: '#dc2626' },
  { bg: 'rgba(249,115,22,0.10)', border: 'rgba(249,115,22,0.85)', badge: '#ea580c' },
  { bg: 'rgba(234,179,8,0.10)', border: 'rgba(234,179,8,0.85)', badge: '#ca8a04' },
  { bg: 'rgba(34,197,94,0.10)', border: 'rgba(34,197,94,0.85)', badge: '#16a34a' },
  { bg: 'rgba(6,182,212,0.10)', border: 'rgba(6,182,212,0.85)', badge: '#0891b2' },
  { bg: 'rgba(99,102,241,0.10)', border: 'rgba(99,102,241,0.85)', badge: '#4f46e5' },
  { bg: 'rgba(217,70,239,0.10)', border: 'rgba(217,70,239,0.85)', badge: '#a21caf' },
  { bg: 'rgba(244,63,94,0.10)', border: 'rgba(244,63,94,0.85)', badge: '#e11d48' },
]

const props = defineProps<{
  entity: EntityPrediction
  colorIndex?: number
}>()

const emit = defineEmits<{
  close: []
}>()

const color = computed(() => ENTITY_COLORS[(props.colorIndex ?? 0) % ENTITY_COLORS.length])
const confidencePercent = computed(() => Math.round(props.entity.confidence * 100))

function copyValue () {
  if (props.entity.value) {
    navigator.clipboard.writeText(props.entity.value)
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 z-50 flex items-center justify-center"
      style="background: rgba(15, 23, 42, 0.18);"
      @click.self="emit('close')"
    >
      <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm mx-4 overflow-hidden">

        <!-- Header -->
        <div
          class="px-5 py-4 flex items-center gap-3"
          :style="{ backgroundColor: color.bg, borderBottom: `2px solid ${color.border}` }"
        >
          <span
            class="text-sm font-bold px-3 py-1 rounded-full text-white"
            :style="{ backgroundColor: color.badge }"
          >{{ entity.entity_name }}</span>
          <button
            class="ml-auto text-slate-400 hover:text-slate-600 transition-colors"
            aria-label="Fermer"
            @click="emit('close')"
          >
            <span class="fr-icon-close-line" style="font-size:18px" aria-hidden="true" />
          </button>
        </div>

        <!-- Body -->
        <div class="p-5 flex flex-col gap-4">

          <!-- Valeur extraite -->
          <div v-if="entity.value" class="flex flex-col gap-1.5">
            <p class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Valeur extraite</p>
            <div class="rounded-xl border border-slate-100 bg-slate-50 px-3 py-2.5 flex items-start justify-between gap-2">
              <p class="text-sm text-slate-700 leading-relaxed break-words flex-1">{{ entity.value }}</p>
              <button
                class="shrink-0 text-slate-300 hover:text-blue-400 transition-colors mt-0.5"
                title="Copier"
                @click="copyValue"
              >
                <span class="fr-icon-draft-line" style="font-size:13px" aria-hidden="true" />
              </button>
            </div>
          </div>

          <!-- Confiance -->
          <div class="flex flex-col gap-1.5">
            <div class="flex justify-between items-center text-sm">
              <span class="font-medium text-slate-600">Confiance</span>
              <span
                class="font-bold text-sm"
                :class="confidencePercent >= 80 ? 'text-emerald-600' : confidencePercent >= 50 ? 'text-amber-500' : 'text-red-500'"
              >{{ confidencePercent }}%</span>
            </div>
            <div class="h-2 rounded-full bg-slate-100 overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-500"
                :class="confidencePercent >= 80 ? 'bg-emerald-500' : confidencePercent >= 50 ? 'bg-amber-400' : 'bg-red-400'"
                :style="{ width: `${confidencePercent}%` }"
              />
            </div>
          </div>

          <!-- Pages -->
          <div v-if="entity.pages?.length" class="flex items-center gap-2 text-sm">
            <span class="font-medium text-slate-600">Pages</span>
            <div class="flex gap-1">
              <span
                v-for="p in entity.pages"
                :key="p"
                class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-600"
              >{{ p + 1 }}</span>
            </div>
          </div>

          <!-- Zones détectées (bbox) -->
          <div v-if="entity.bbox?.length" class="flex flex-col gap-1.5">
            <p class="text-xs font-semibold text-slate-500 uppercase tracking-wide">
              {{ entity.bbox.length }} zone{{ entity.bbox.length > 1 ? 's' : '' }} détectée{{ entity.bbox.length > 1 ? 's' : '' }}
            </p>
            <div class="flex flex-col gap-2 max-h-40 overflow-y-auto">
              <div
                v-for="(bbox, idx) in entity.bbox"
                :key="idx"
                class="rounded-xl border border-slate-100 bg-slate-50 px-3 py-2 text-xs text-slate-700"
              >
                <div class="flex items-center justify-between gap-2">
                  <span v-if="bbox.text" class="font-medium truncate flex-1">« {{ bbox.text }} »</span>
                  <span class="text-slate-400 shrink-0">{{ Math.round(bbox.confidence * 100) }}%</span>
                </div>
                <div class="flex gap-3 mt-1 text-[10px] text-slate-400 font-mono">
                  <span>x: {{ bbox.x.toFixed(3) }}</span>
                  <span>y: {{ bbox.y.toFixed(3) }}</span>
                  <span>{{ bbox.width.toFixed(3) }} × {{ bbox.height.toFixed(3) }}</span>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  </Teleport>
</template>
