<script setup lang="ts">
import { computed, ref } from 'vue'
import type { PageLabel } from '@/interfaces/classification'
import { isValidSlug, toSlug } from '@/interfaces/classification'
import PredictionDetailModal from '@/components/PredictionDetailModal.vue'
import AnnotationLabelModal from '@/components/AnnotationLabelModal.vue'

const props = defineProps<{
  modelValue: PageLabel[]
  predefinedLabels?: PageLabel[]
  consentForTraining: boolean | null
}>()

const emit = defineEmits<{
  'update:modelValue': [labels: PageLabel[]]
  'update:consentForTraining': [value: boolean | null]
  'save': []
}>()

// --- Detail modal ---
const detailLabel = ref<PageLabel | null>(null)
const editLabel = ref<PageLabel | null>(null)

// --- Free-form form state ---
const freeKey = ref('')
const freeDefinition = ref('')
const showFreeForm = ref(false)

const slugPreview = computed(() => toSlug(freeKey.value))

const keyError = computed(() => {
  if (!freeKey.value) return null
  if (!isValidSlug(slugPreview.value)) return 'Le label doit commencer par une lettre ou un chiffre.'
  if (props.modelValue.some(l => l.key === slugPreview.value)) return 'Ce label est déjà ajouté.'
  return null
})

const canAddFree = computed(() =>
  freeKey.value.trim().length > 0
  && freeDefinition.value.trim().length > 0
  && isValidSlug(slugPreview.value)
  && !props.modelValue.some(l => l.key === slugPreview.value),
)

function isSelected (key: string) {
  return props.modelValue.some(l => l.key === key)
}

function togglePredefined (label: PageLabel) {
  if (isSelected(label.key)) {
    emit('update:modelValue', props.modelValue.filter(l => l.key !== label.key))
  }
  else {
    emit('update:modelValue', [...props.modelValue, label])
  }
}

function removeLabel (key: string) {
  emit('update:modelValue', props.modelValue.filter(l => l.key !== key))
}

function onAnnotationSave (oldKey: string, updated: PageLabel) {
  emit('update:modelValue', props.modelValue.map(l => l.key === oldKey ? updated : l))
  editLabel.value = null
}

function onAnnotationDelete (key: string) {
  emit('update:modelValue', props.modelValue.filter(l => l.key !== key))
  editLabel.value = null
}

function onPredictionValidate (key: string, validation: 'valid' | 'invalid' | null) {
  emit('update:modelValue', props.modelValue.map(l =>
    l.key === key ? { ...l, validation } : l,
  ))
}

function addFreeLabel () {
  if (!canAddFree.value) return
  emit('update:modelValue', [
    ...props.modelValue,
    { key: slugPreview.value, definition: freeDefinition.value.trim(), predefined: false },
  ])
  freeKey.value = ''
  freeDefinition.value = ''
  showFreeForm.value = false
}
</script>

<template>
  <div class="rounded-2xl border border-slate-200 bg-white shadow-sm text-sm">
    <!-- Header -->
    <div class="flex items-center gap-2 px-4 py-3 border-b border-slate-100">
      <span class="fr-icon-price-tag-3-line text-slate-400" style="font-size:14px" aria-hidden="true" />
      <span class="font-semibold text-slate-700 text-sm">Classification de la page</span>
      <span
        v-if="modelValue.length"
        class="ml-auto text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-100 text-blue-700"
      >{{ modelValue.length }}</span>
    </div>

    <div class="p-3 flex flex-col gap-3">

      <!-- Consentement : segment control -->
      <div class="flex items-center gap-3">
        <span class="text-xs text-slate-400 w-16 shrink-0">Consentement</span>
        <div class="flex flex-1 rounded-xl overflow-hidden border border-slate-200 text-[11px] font-semibold">
          <button
            class="flex-1 py-1.5 flex items-center justify-center gap-1 transition-colors"
            :class="consentForTraining === true ? 'bg-emerald-500 text-white' : 'bg-white text-slate-400 hover:bg-slate-50'"
            @click.stop="emit('update:consentForTraining', consentForTraining === true ? null : true)"
          >
            <span class="fr-icon-lock-unlock-line" style="font-size:10px" aria-hidden="true" />
            Autorisé
          </button>
          <button
            class="flex-1 py-1.5 flex items-center justify-center gap-1 transition-colors border-l border-slate-200"
            :class="consentForTraining === false ? 'bg-rose-500 text-white' : 'bg-white text-slate-400 hover:bg-slate-50'"
            @click.stop="emit('update:consentForTraining', consentForTraining === false ? null : false)"
          >
            <span class="fr-icon-lock-line" style="font-size:10px" aria-hidden="true" />
            Exclu
          </button>
        </div>
      </div>
      <p class="text-[10px] pl-[76px] -mt-1.5">
        <span v-if="consentForTraining === true" class="text-emerald-600 font-medium">✓ Page partagée pour améliorer le modèle</span>
        <span v-else-if="consentForTraining === false" class="text-rose-500 font-medium">✗ Page exclue du réentraînement</span>
        <span v-else class="text-slate-400 italic">Aucun consentement défini</span>
      </p>

      <!-- Labels actifs -->
      <div v-if="modelValue.length" class="flex flex-wrap gap-1.5">
        <div
          v-for="label in modelValue"
          :key="label.key"
          class="flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium"
          :class="[
            label.readonly
              ? 'bg-amber-50 border-amber-300 text-amber-700 hover:bg-amber-100 cursor-pointer'
              : label.predefined
                ? 'group bg-blue-50 border-blue-200 text-blue-700 cursor-pointer hover:bg-blue-100'
                : 'group bg-violet-50 border-violet-200 text-violet-700 cursor-pointer hover:bg-violet-100',
          ]"
          :title="label.readonly ? 'Prédiction automatique — cliquez pour les détails' : 'Cliquez pour modifier'"
          @click="label.readonly ? (detailLabel = label) : (editLabel = label)"
        >
          <span v-if="label.readonly" class="fr-icon-robot-2-line shrink-0" style="font-size:9px" aria-hidden="true" />
          <span v-if="label.readonly && label.validation === 'valid'" class="text-emerald-500 shrink-0" style="font-size:9px" aria-hidden="true">✓</span>
          <span v-if="label.readonly && label.validation === 'invalid'" class="text-red-400 shrink-0" style="font-size:9px" aria-hidden="true">✗</span>
          <span>{{ label.key }}</span>
          <button
            v-if="!label.readonly"
            class="opacity-40 group-hover:opacity-100 hover:text-red-500 transition-opacity"
            aria-label="Retirer"
            @click.stop="removeLabel(label.key)"
          >
            <span class="fr-icon-close-line" style="font-size:9px" aria-hidden="true" />
          </button>
        </div>
      </div>
      <p v-else class="text-slate-400 italic text-xs text-center py-1">Aucune classification</p>

      <!-- Modal détail prédiction (hors flux DOM via Teleport interne) -->
      <PredictionDetailModal
        v-if="detailLabel"
        :label="detailLabel"
        @close="detailLabel = null"
        @validate="onPredictionValidate"
      />

      <!-- Modal édition annotation manuelle -->
      <AnnotationLabelModal
        v-if="editLabel"
        :label="editLabel"
        @close="editLabel = null"
        @save="onAnnotationSave"
        @delete="onAnnotationDelete"
      />

      <!-- Labels prédéfinis -->
      <div v-if="predefinedLabels?.length" class="flex flex-wrap gap-1.5">
        <button
          v-for="label in predefinedLabels"
          :key="label.key"
          class="flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium transition-all"
          :class="isSelected(label.key)
            ? 'bg-blue-500 border-blue-500 text-white'
            : 'border-slate-200 text-slate-500 hover:border-blue-300 hover:bg-blue-50 hover:text-blue-600'"
          :title="label.definition"
          @click="togglePredefined(label)"
        >
          <span v-if="isSelected(label.key)" class="fr-icon-checkbox-line" style="font-size:9px" aria-hidden="true" />
          {{ label.key }}
        </button>
      </div>

      <!-- Label libre -->
      <div>
        <button
          class="flex items-center gap-1 text-xs font-medium text-slate-400 hover:text-violet-600 transition-colors"
          @click="showFreeForm = !showFreeForm"
        >
          <span :class="showFreeForm ? 'fr-icon-subtract-line' : 'fr-icon-add-line'" style="font-size:10px" aria-hidden="true" />
          Label libre
        </button>
        <Transition name="expand">
          <div v-if="showFreeForm" class="mt-2 flex flex-col gap-2">
            <input
              v-model="freeKey"
              type="text"
              placeholder="ex: facture_energie"
              class="w-full rounded-lg border px-2.5 py-1.5 text-xs outline-none transition"
              :class="freeKey && keyError ? 'border-red-300 focus:ring-red-100' : 'border-slate-200 focus:border-violet-400 focus:ring-2 focus:ring-violet-100'"
            >
            <span v-if="freeKey && !keyError" class="text-violet-500 text-xs">→ <code>{{ slugPreview }}</code></span>
            <span v-if="keyError" class="text-red-500 text-xs">{{ keyError }}</span>
            <textarea
              v-model="freeDefinition"
              rows="2"
              placeholder="Définition..."
              class="w-full resize-none rounded-lg border border-slate-200 px-2.5 py-1.5 text-xs outline-none focus:border-violet-400 focus:ring-2 focus:ring-violet-100 transition"
            />
            <button
              class="flex items-center justify-center gap-1 rounded-lg px-3 py-1.5 text-xs font-semibold transition-all"
              :class="canAddFree ? 'bg-violet-600 text-white hover:bg-violet-700' : 'bg-slate-100 text-slate-400 cursor-default'"
              :disabled="!canAddFree"
              @click="addFreeLabel"
            >
              <span class="fr-icon-add-line" style="font-size:10px" aria-hidden="true" />
              Ajouter
            </button>
          </div>
        </Transition>
      </div>

      <!-- Enregistrer -->
      <button
        class="w-full flex items-center justify-center gap-1.5 rounded-xl bg-blue-600 px-3 py-2 text-xs font-bold text-white hover:bg-blue-700 transition-colors"
        @click="emit('save')"
      >
        <span class="fr-icon-save-line" style="font-size:12px" aria-hidden="true" />
        Enregistrer
      </button>
    </div>
  </div>
</template>

<style scoped>
.expand-enter-active,
.expand-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>


