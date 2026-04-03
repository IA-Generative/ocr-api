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
  <div class="w-72 shrink-0 rounded-2xl border border-slate-200 bg-white shadow-xl text-sm flex flex-col sticky top-4">
    <!-- Header compact -->
    <div class="flex items-center justify-between px-3 py-2.5 border-b border-slate-100">
      <div class="flex items-center gap-2">
        <span
          v-if="isDrawn"
          class="text-xs font-semibold px-2 py-0.5 rounded-full bg-violet-100 text-violet-700"
        >✏️ Annotée</span>
        <span v-else class="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
          OCR
        </span>
        <span
          class="font-bold tabular-nums text-sm"
          :class="confidenceColor(box.confidence)"
        >{{ (box.confidence * 100).toFixed(0) }}%</span>
      </div>
      <div class="flex items-center gap-1">
        <button
          class="rounded-lg p-1.5 transition-colors"
          :class="isHidden ? 'bg-slate-700 text-white' : 'text-slate-400 hover:bg-slate-100'"
          :title="isHidden ? 'Afficher' : 'Masquer'"
          @click="emit('toggleVisibility')"
        >
          <span :class="isHidden ? 'fr-icon-eye-line' : 'fr-icon-eye-off-line'" style="font-size:13px" aria-hidden="true" />
        </button>
        <button
          class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 transition-colors"
          aria-label="Fermer"
          @click="emit('close')"
        >
          <span class="fr-icon-close-line" style="font-size:13px" aria-hidden="true" />
        </button>
      </div>
    </div>

    <div class="flex flex-col gap-3 p-3">
      <!-- Texte original (non dessiné) -->
      <div v-if="!isDrawn" class="rounded-lg bg-slate-50 border border-slate-100 px-2.5 py-2 flex items-start justify-between gap-2">
        <p class="text-slate-500 italic text-xs leading-snug line-clamp-2 flex-1">{{ box.text || '—' }}</p>
        <button
          class="shrink-0 text-slate-300 hover:text-blue-500 transition-colors"
          title="Copier"
          @click="copyText()"
        >
          <span class="fr-icon-draft-line" style="font-size:12px" aria-hidden="true" />
        </button>
      </div>

      <!-- Correction / saisie -->
      <textarea
        v-model="correctedText"
        rows="2"
        class="w-full resize-none rounded-lg border border-slate-200 bg-white px-2.5 py-2 text-slate-700 text-xs outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 transition"
        :placeholder="isDrawn ? 'Texte de la zone...' : 'Corriger le texte...'"
      />

      <!-- Toggles : privée + validation -->
      <div class="rounded-xl border border-slate-100 bg-slate-50 divide-y divide-slate-100">
        <!-- Privée -->
        <div class="flex items-center justify-between px-3 py-2.5">
          <div>
            <p class="text-xs font-semibold text-slate-700">{{ isPrivate ? '🔒 Privée' : '🔓 Publique' }}</p>
            <p class="text-xs text-slate-400 mt-0.5">{{ isPrivate ? 'Exclue du réentraînement' : 'Partagée pour améliorer le modèle' }}</p>
          </div>
          <div
            class="relative shrink-0 cursor-pointer rounded-full transition-colors duration-200"
            style="width:40px;height:22px"
            :style="{ backgroundColor: isPrivate ? '#f43f5e' : '#10b981' }"
            @click.stop="isPrivate = !isPrivate"
          >
            <div
              class="absolute top-px rounded-full bg-white shadow transition-transform duration-200"
              style="width:18px;height:18px;top:2px"
              :style="{ transform: isPrivate ? 'translateX(20px)' : 'translateX(2px)' }"
            />
          </div>
        </div>
        <!-- Validation OCR -->
        <div v-if="!isDrawn" class="flex items-center justify-between px-3 py-2.5">
          <div>
            <p class="text-xs font-semibold text-slate-700">{{ validation === 'valid' ? '✅ Valide' : '❌ Invalide' }}</p>
            <p class="text-xs text-slate-400 mt-0.5">Qualité de la détection OCR</p>
          </div>
          <div
            class="relative shrink-0 cursor-pointer rounded-full transition-colors duration-200"
            style="width:40px;height:22px"
            :style="{ backgroundColor: validation === 'valid' ? '#10b981' : '#ef4444' }"
            @click.stop="validation = validation === 'valid' ? 'invalid' : 'valid'"
          >
            <div
              class="absolute rounded-full bg-white shadow transition-transform duration-200"
              style="width:18px;height:18px;top:2px"
              :style="{ transform: validation === 'valid' ? 'translateX(20px)' : 'translateX(2px)' }"
            />
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex gap-2">
        <button
          class="flex-1 flex items-center justify-center gap-1.5 rounded-xl px-3 py-2 text-xs font-bold transition-all"
          :class="justSaved
            ? 'bg-emerald-500 text-white'
            : isDirty
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-slate-100 text-slate-400 cursor-default'"
          :disabled="!isDirty && !justSaved"
          @click="onSave"
        >
          <span :class="justSaved ? 'fr-icon-check-line' : 'fr-icon-save-line'" style="font-size:12px" aria-hidden="true" />
          {{ justSaved ? 'Enregistré !' : 'Enregistrer' }}
        </button>
        <button
          v-if="isDrawn"
          class="flex items-center justify-center gap-1 rounded-xl border border-red-200 px-3 py-2 text-xs font-medium text-red-400 hover:bg-red-50 hover:border-red-400 transition-all"
          @click="emit('delete')"
        >
          <span class="fr-icon-delete-line" style="font-size:12px" aria-hidden="true" />
        </button>
      </div>
    </div>
  </div>
</template>
