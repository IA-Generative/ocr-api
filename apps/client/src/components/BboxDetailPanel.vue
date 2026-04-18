<script setup lang="ts">
import type { components } from '@/api/types/api.schema'
import { computed, ref, watch } from 'vue'
import type { BboxReview, ValidationState } from '@/interfaces/review'
import type { DrawnBox } from '@/composables/use-box-drawing'

type Bbox = components['schemas']['Bbox']

const props = defineProps<{
  box: Bbox | DrawnBox
  savedState?: BboxReview
  isHidden?: boolean
}>()

const isDrawn = computed(() => 'isDrawn' in props.box && props.box.isDrawn)

const emit = defineEmits<{
  close: []
  save: [review: BboxReview]
  delete: []
  copy: [text: string]
  toggleVisibility: []
}>()

function copyText () {
  navigator.clipboard.writeText(correctedText.value)
}

const validation = ref<ValidationState>(props.savedState?.validation ?? (isDrawn.value ? null : 'valid'))
const correctedText = ref(props.savedState?.correctedText ?? props.box.text)
const isPrivate = ref<boolean | null>(props.savedState?.isPrivate ?? (isDrawn.value ? null : false))

watch(() => [props.box, props.savedState] as const, ([newBox, newSaved]) => {
  const _isDrawn = 'isDrawn' in newBox && newBox.isDrawn
  validation.value = newSaved?.validation ?? (_isDrawn ? null : 'valid')
  correctedText.value = newSaved?.correctedText ?? newBox.text
  isPrivate.value = newSaved?.isPrivate ?? (_isDrawn ? null : false)
  savedSnapshot.value = JSON.stringify({ correctedText: newSaved?.correctedText ?? newBox.text, validation: newSaved?.validation ?? (_isDrawn ? null : 'valid'), isPrivate: newSaved?.isPrivate ?? (_isDrawn ? null : false) })
  justSaved.value = false
})

const confidenceColor = (confidence: number) => {
  if (confidence >= 0.9) return 'text-emerald-600'
  if (confidence >= 0.7) return 'text-amber-500'
  return 'text-red-500'
}

const savedSnapshot = ref<string>(JSON.stringify({ correctedText: props.savedState?.correctedText ?? props.box.text, validation: props.savedState?.validation ?? (isDrawn.value ? null : 'valid'), isPrivate: props.savedState?.isPrivate ?? (isDrawn.value ? null : false) }))
const justSaved = ref(false)
let _savedTimeout: any = null

const isDirty = computed(() => {
  const snap = JSON.parse(savedSnapshot.value)
  return correctedText.value !== snap.correctedText || validation.value !== snap.validation || isPrivate.value !== snap.isPrivate
})

function onSave () {
  emit('save', { correctedText: correctedText.value, validation: validation.value, isPrivate: isPrivate.value ?? false })
  savedSnapshot.value = JSON.stringify({ correctedText: correctedText.value, validation: validation.value, isPrivate: isPrivate.value })
  justSaved.value = true
  clearTimeout(_savedTimeout)
  _savedTimeout = setTimeout(() => { justSaved.value = false }, 2000)
}
</script>

<template>
  <div class="w-72 shrink-0 rounded-2xl border border-slate-100 bg-white shadow-xl text-sm flex flex-col sticky top-4 overflow-hidden">

    <!-- Header -->
    <div class="flex items-center justify-between px-4 py-3 border-b border-slate-100">
      <div class="flex items-center gap-2">
        <span
          v-if="isDrawn"
          class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-violet-100 text-violet-600 tracking-wide uppercase"
        >Annotée</span>
        <span v-else class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-500 tracking-wide uppercase">OCR</span>
        <span
          class="font-bold tabular-nums text-sm"
          :class="confidenceColor(box.confidence)"
        >{{ (box.confidence * 100).toFixed(0) }}%</span>
      </div>
      <div class="flex items-center gap-0.5">
        <button
          class="w-7 h-7 flex items-center justify-center rounded-lg transition-colors"
          :class="isHidden ? 'bg-slate-800 text-white' : 'text-slate-400 hover:bg-slate-100'"
          :title="isHidden ? 'Afficher' : 'Masquer'"
          @click="emit('toggleVisibility')"
        >
          <span :class="isHidden ? 'fr-icon-eye-line' : 'fr-icon-eye-off-line'" style="font-size:12px" aria-hidden="true" />
        </button>
        <button
          class="w-7 h-7 flex items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100 transition-colors"
          aria-label="Fermer"
          @click="emit('close')"
        >
          <span class="fr-icon-close-line" style="font-size:12px" aria-hidden="true" />
        </button>
      </div>
    </div>

    <div class="flex flex-col gap-3 p-4">

      <!-- Texte original -->
      <div v-if="!isDrawn" class="rounded-xl bg-slate-50 border border-slate-100 px-3 py-2.5 flex items-start justify-between gap-2">
        <p class="text-slate-400 italic text-xs leading-relaxed line-clamp-2 flex-1">{{ box.text || '—' }}</p>
        <button
          class="shrink-0 text-slate-300 hover:text-blue-400 transition-colors mt-0.5"
          title="Copier"
          @click="copyText()"
        >
          <span class="fr-icon-draft-line" style="font-size:11px" aria-hidden="true" />
        </button>
      </div>

      <!-- Correction -->
      <textarea
        v-model="correctedText"
        rows="2"
        class="w-full resize-none rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-slate-700 text-xs outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 transition leading-relaxed"
        :placeholder="isDrawn ? 'Texte de la zone…' : 'Corriger le texte…'"
      />

      <!-- Segment controls -->
      <div class="flex flex-col gap-2">

        <!-- Données -->
        <div class="flex items-center gap-3">
          <span class="text-xs text-slate-400 w-16 shrink-0">Données</span>
          <div class="flex flex-1 rounded-xl overflow-hidden border border-slate-200 text-[11px] font-semibold">
            <button
              class="flex-1 py-1.5 flex items-center justify-center gap-1 transition-colors"
              :class="!isPrivate
                ? 'bg-emerald-500 text-white'
                : 'bg-white text-slate-400 hover:bg-slate-50'"
              @click.stop="isPrivate = false"
            >
              <span class="fr-icon-lock-unlock-line" style="font-size:10px" aria-hidden="true" />
              Publique
            </button>
            <button
              class="flex-1 py-1.5 flex items-center justify-center gap-1 transition-colors border-l border-slate-200"
              :class="isPrivate
                ? 'bg-rose-500 text-white'
                : 'bg-white text-slate-400 hover:bg-slate-50'"
              @click.stop="isPrivate = true"
            >
              <span class="fr-icon-lock-line" style="font-size:10px" aria-hidden="true" />
              Privée
            </button>
          </div>
        </div>

        <!-- Détection -->
        <div v-if="!isDrawn" class="flex items-center gap-3">
          <span class="text-xs text-slate-400 w-16 shrink-0">Détection</span>
          <div class="flex flex-1 rounded-xl overflow-hidden border border-slate-200 text-[11px] font-semibold">
            <button
              class="flex-1 py-1.5 flex items-center justify-center gap-1 transition-colors"
              :class="validation === 'valid'
                ? 'bg-emerald-500 text-white'
                : 'bg-white text-slate-400 hover:bg-slate-50'"
              @click.stop="validation = 'valid'"
            >
              <span class="fr-icon-checkbox-circle-line" style="font-size:10px" aria-hidden="true" />
              Valide
            </button>
            <button
              class="flex-1 py-1.5 flex items-center justify-center gap-1 transition-colors border-l border-slate-200"
              :class="validation === 'invalid'
                ? 'bg-red-500 text-white'
                : 'bg-white text-slate-400 hover:bg-slate-50'"
              @click.stop="validation = 'invalid'"
            >
              <span class="fr-icon-close-circle-line" style="font-size:10px" aria-hidden="true" />
              Invalide
            </button>
          </div>
        </div>

      </div>

      <!-- Actions -->
      <div class="flex gap-2 pt-1">
        <button
          class="flex-1 flex items-center justify-center gap-1.5 rounded-xl px-3 py-2 text-xs font-bold transition-all"
          :class="justSaved
            ? 'bg-emerald-500 text-white'
            : isDirty
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-slate-100 text-slate-300 cursor-default'"
          :disabled="!isDirty && !justSaved"
          @click="onSave"
        >
          <span :class="justSaved ? 'fr-icon-check-line' : 'fr-icon-save-line'" style="font-size:11px" aria-hidden="true" />
          {{ justSaved ? 'Enregistré !' : 'Enregistrer' }}
        </button>
        <button
          v-if="isDrawn"
          class="w-9 flex items-center justify-center rounded-xl border border-red-100 text-red-300 hover:bg-red-50 hover:border-red-300 hover:text-red-500 transition-all"
          title="Supprimer"
          @click="emit('delete')"
        >
          <span class="fr-icon-delete-line" style="font-size:12px" aria-hidden="true" />
        </button>
      </div>

    </div>
  </div>
</template>
