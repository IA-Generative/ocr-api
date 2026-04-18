<template>
  <div class="flex flex-col gap-4">
    <div class="flex items-center justify-between">
      <h3 class="fr-h5 mb-0">Entités extraites</h3>
      <span class="px-2 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-600">
        {{ entities.length }} résultat{{ entities.length !== 1 ? 's' : '' }}
      </span>
    </div>

    <!-- Aucun résultat -->
    <div
      v-if="entities.length === 0"
      class="flex flex-col items-center gap-2 rounded-xl border-2 border-dashed border-slate-200 py-10 text-slate-400"
    >
      <span class="fr-icon-search-line" style="font-size: 28px;" aria-hidden="true" />
      <p class="text-sm">Aucune entité trouvée dans le document</p>
    </div>

    <!-- Résultats groupés par entité -->
    <div v-else class="flex flex-col gap-3">
      <div
        v-for="(group, name) in grouped"
        :key="name"
        class="rounded-xl border border-slate-200 bg-white overflow-hidden shadow-sm"
      >
        <!-- Header de groupe -->
        <div class="flex items-center gap-2 px-4 py-2.5 border-b border-slate-100 bg-slate-50">
          <span
            class="shrink-0 px-2 py-0.5 rounded-full text-xs font-semibold"
            :style="colorFor(name)"
          >
            {{ name }}
          </span>
          <span class="text-xs text-slate-500 ml-auto">{{ group.length }} occurrence{{ group.length !== 1 ? 's' : '' }}</span>
        </div>

        <!-- Valeurs -->
        <div class="divide-y divide-slate-50">
          <div
            v-for="(entity, i) in group"
            :key="i"
            class="flex items-center gap-3 px-4 py-2.5"
          >
            <!-- Valeur -->
            <span class="flex-1 text-sm text-slate-800 font-medium">
              {{ entity.value ?? '—' }}
            </span>

            <!-- Pages -->
            <div v-if="entity.pages?.length" class="flex items-center gap-1 shrink-0">
              <span
                v-for="p in entity.pages"
                :key="p"
                class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-500"
              >
                p.{{ p }}
              </span>
            </div>

            <!-- Localisation bbox -->
            <span
              v-if="entity.bbox?.length"
              class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium bg-blue-50 text-blue-600 shrink-0"
              :title="`${entity.bbox.length} zone${entity.bbox.length > 1 ? 's' : ''} détectée${entity.bbox.length > 1 ? 's' : ''}`"
            >
              <span class="fr-icon-map-pin-2-line" style="font-size:10px" aria-hidden="true" />
              {{ entity.bbox.length }}
            </span>

            <!-- Barre de confiance -->
            <div class="flex items-center gap-2 shrink-0 w-28">
              <div class="flex-1 h-1.5 rounded-full bg-slate-100 overflow-hidden">
                <div
                  class="h-full rounded-full transition-all"
                  :class="confidenceColor(entity.confidence)"
                  :style="{ width: `${Math.round(entity.confidence * 100)}%` }"
                />
              </div>
              <span class="text-[10px] text-slate-400 w-7 text-right">
                {{ Math.round(entity.confidence * 100) }}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

export type EntityPrediction = {
  entity_name: string
  confidence: number
  value?: string | null
  bbox?: { x: number; y: number; width: number; height: number; text: string; confidence: number }[] | null
  pages?: number[] | null
}

const props = defineProps<{
  entities: EntityPrediction[]
}>()

const grouped = computed(() => {
  const result: Record<string, EntityPrediction[]> = {}
  for (const e of props.entities) {
    if (!result[e.entity_name]) result[e.entity_name] = []
    result[e.entity_name].push(e)
  }
  return result
})

const PALETTE = [
  { bg: '#eff6ff', color: '#1d4ed8' },
  { bg: '#fdf4ff', color: '#7e22ce' },
  { bg: '#fff7ed', color: '#c2410c' },
  { bg: '#f0fdf4', color: '#15803d' },
  { bg: '#fff1f2', color: '#be123c' },
  { bg: '#f0fdfa', color: '#0f766e' },
  { bg: '#fefce8', color: '#a16207' },
  { bg: '#f0f9ff', color: '#0369a1' },
]
const colorCache = new Map<string, { bg: string; color: string }>()
function colorFor(name: string) {
  if (!colorCache.has(name)) {
    colorCache.set(name, PALETTE[colorCache.size % PALETTE.length])
  }
  return colorCache.get(name)!
}

function confidenceColor(confidence: number) {
  if (confidence >= 0.8) return 'bg-emerald-400'
  if (confidence >= 0.5) return 'bg-amber-400'
  return 'bg-rose-400'
}
</script>
