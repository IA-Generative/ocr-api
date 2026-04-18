<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 z-50 flex items-center justify-center"
      @click.self="emit('close')"
    >
      <div class="w-80 rounded-2xl bg-white shadow-2xl flex flex-col overflow-hidden border border-slate-100">

        <!-- Header -->
        <div class="flex items-center justify-between px-4 py-3 border-b border-amber-100 bg-amber-50">
          <div class="flex items-center gap-2">
            <span class="fr-icon-robot-2-line text-amber-500" style="font-size:14px" aria-hidden="true" />
            <span class="text-[11px] font-bold text-amber-700 tracking-wide uppercase">Prédiction auto</span>
          </div>
          <button
            class="w-7 h-7 flex items-center justify-center rounded-lg text-slate-400 hover:bg-amber-100 transition-colors"
            aria-label="Fermer"
            @click="emit('close')"
          >
            <span class="fr-icon-close-line" style="font-size:12px" aria-hidden="true" />
          </button>
        </div>

        <div class="p-4 flex flex-col gap-3">

          <!-- Label -->
          <div class="flex flex-col gap-0.5">
            <span class="text-xs text-slate-400">Label</span>
            <span class="text-base font-bold text-slate-900">{{ label.key }}</span>
            <span v-if="label.definition" class="text-xs text-slate-500">{{ label.definition }}</span>
          </div>

          <!-- Confiance -->
          <div v-if="label.confidence !== undefined" class="flex items-center gap-3">
            <span class="text-xs text-slate-400 w-16 shrink-0">Confiance</span>
            <div class="flex-1 h-2 rounded-full bg-slate-100 overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-500"
                :class="label.confidence >= 0.75 ? 'bg-emerald-500' : label.confidence >= 0.5 ? 'bg-amber-400' : 'bg-red-400'"
                :style="{ width: `${Math.round(label.confidence * 100)}%` }"
              />
            </div>
            <span
              class="text-xs font-bold w-10 text-right tabular-nums"
              :class="label.confidence >= 0.75 ? 'text-emerald-600' : label.confidence >= 0.5 ? 'text-amber-600' : 'text-red-500'"
            >{{ Math.round(label.confidence * 100) }}%</span>
          </div>

          <!-- Modèle -->
          <div v-if="label.model" class="rounded-xl border border-slate-100 bg-slate-50 px-3 py-2.5">
            <div class="grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
              <span class="text-slate-400">Modèle</span>
              <span class="text-slate-700 font-medium truncate" :title="label.model.name">{{ label.model.name }}</span>
              <span class="text-slate-400">Version</span>
              <span class="text-slate-700 font-medium">{{ label.model.version }}</span>
              <template v-if="label.model.device">
                <span class="text-slate-400">Device</span>
                <span class="text-slate-700 font-medium">{{ label.model.device }}</span>
              </template>
            </div>
          </div>

          <p class="text-[10px] text-slate-400 italic">Ce label est automatique et ne peut pas être supprimé.</p>

          <!-- Validation -->
          <div class="flex flex-col gap-2 pt-1 border-t border-slate-100">
            <div class="flex items-center gap-3">
              <span class="text-xs text-slate-400 w-16 shrink-0">Votre avis</span>
              <div class="flex flex-1 rounded-xl overflow-hidden border border-slate-200 text-[11px] font-semibold">
                <button
                  class="flex-1 py-1.5 flex items-center justify-center gap-1 transition-colors"
                  :class="validation === 'valid' ? 'bg-emerald-500 text-white' : 'bg-white text-slate-400 hover:bg-slate-50'"
                  @click="setValidation(validation === 'valid' ? null : 'valid')"
                >
                  <span class="fr-icon-checkbox-circle-line" style="font-size:10px" aria-hidden="true" />
                  Valider
                </button>
                <button
                  class="flex-1 py-1.5 flex items-center justify-center gap-1 transition-colors border-l border-slate-200"
                  :class="validation === 'invalid' ? 'bg-red-500 text-white' : 'bg-white text-slate-400 hover:bg-slate-50'"
                  @click="setValidation(validation === 'invalid' ? null : 'invalid')"
                >
                  <span class="fr-icon-close-circle-line" style="font-size:10px" aria-hidden="true" />
                  Invalider
                </button>
              </div>
            </div>
            <p v-if="validation" class="text-[10px] text-slate-400 italic text-center">
              {{ validation === 'valid' ? '✅ Prédiction validée' : '❌ Prédiction invalidée' }}
            </p>
          </div>

        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { PageLabel } from '@/interfaces/classification'

const props = defineProps<{
  label: PageLabel
}>()

const emit = defineEmits<{
  close: []
  validate: [key: string, validation: 'valid' | 'invalid' | null]
}>()

const validation = ref<'valid' | 'invalid' | null>(props.label.validation ?? null)

function setValidation (value: 'valid' | 'invalid' | null) {
  validation.value = value
  emit('validate', props.label.key, value)
}
</script>
